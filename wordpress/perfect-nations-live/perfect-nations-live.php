<?php
/**
 * Plugin Name:       Perfect Nations Live Pages
 * Description:       Serves each Perfect Nations page from the Perfect Nations GitHub repository, so a page updates without copying and pasting its code. Pages stay in Elementor; if GitHub cannot be reached, the page shows the code pasted in its widget.
 * Version:           1.3.0
 * Requires at least: 6.0
 * Requires PHP:      7.4
 * Author:            Perfect Nations
 * License:           GPL-2.0-or-later
 * Text Domain:       pn-live
 *
 * How it works
 * 1. pages/manifest.json in the repository lists each live page by the id of its root element
 *    (for example "pn-bp-barbados") and the file that holds its code (pages/blueprint-barbados.html).
 * 2. When WordPress renders an Elementor Custom HTML widget (or a Custom HTML block) whose code
 *    contains one of those ids, the plugin serves the repository file in its place.
 * 3. v1.2 (speed): visitors are always served the stored copy, so no page view waits for GitHub.
 *    The stored copies are brought up to date in the background: GitHub calls the site after every
 *    change to main (POST /wp-json/pn-live/v1/refresh, at most once a minute), and the site also
 *    checks by itself every ten minutes. A check reads main's latest commit from github.com; only
 *    when it moved are the listed files read again, at that exact commit, each with its ETag (an
 *    unchanged file costs a 304). When any file changed, the page cache is cleared once.
 *    Pages therefore stay in the LiteSpeed page cache for a week, or until their code changes,
 *    instead of the ten minutes of 1.1. If nothing has ever been fetched, the pasted code is shown.
 * 4. Settings > Perfect Nations Live: what is live, Refresh now, and Export page code.
 * 6. v1.3: when the manifest names {"additional_css": {"file": "pages/additional.css"}}, that file is served
 *    as the sitewide Additional CSS, in place of the copy kept in Appearance > Customize > Additional CSS
 *    (which stays untouched, as the fallback). If that WordPress copy is edited after the switch, the
 *    WordPress copy wins, until Settings > Perfect Nations Live > Use the GitHub copy again is pressed.
 * 5. v1.1: a manifest key may name one post, "pn-disp@post-slug", so posts that share a root id
 *    (dispatches, a duplicate widget) can each be served on their own; and the manifest may list
 *    same-site redirects, {"redirects": {"/old-path/": "/new-path/"}}, answered with a 301.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

final class PN_Live_Pages {

	const VERSION  = '1.3.0';
	const REPO     = 'preetisinha70-PN/perfect-nations';
	const BRANCH   = 'main';
	const MANIFEST = 'pages/manifest.json';
	const TTL      = 600;      // seconds between the site's own background checks of GitHub
	const PAGE_TTL = 604800;   // seconds a served page may stay in the page cache (a week); a code change clears it sooner
	const PING_GAP = 60;       // GitHub may ask for a check at most once a minute
	const RETRY    = 120;      // seconds to wait after a failed fetch before trying again
	const MAX      = 2500000;  // largest file accepted, in bytes
	const OPT      = 'pn_live_';

	/** @var PN_Live_Pages|null */
	private static $instance = null;

	/** @var array|null */
	private $manifest = null;

	/** @var array */
	private $served = array();

	/** @var bool */
	private $refreshing = false;

	public static function instance() {
		if ( null === self::$instance ) {
			self::$instance = new self();
		}
		return self::$instance;
	}

	private function __construct() {
		add_filter( 'elementor/widget/render_content', array( $this, 'filter_widget' ), 20, 2 );
		add_filter( 'render_block', array( $this, 'filter_block' ), 20, 2 );
		add_filter( 'elementor/element/is_dynamic_content', array( $this, 'not_cached' ), 20, 2 );
		add_shortcode( 'pn_live', array( $this, 'shortcode' ) );
		add_action( 'template_redirect', array( $this, 'redirects' ), 1 );
		add_action( 'admin_menu', array( $this, 'admin_menu' ) );
		add_action( 'admin_post_pn_live_refresh', array( $this, 'handle_refresh' ) );
		add_action( 'admin_post_pn_live_export', array( $this, 'handle_export' ) );
		add_action( 'admin_post_pn_live_toggle', array( $this, 'handle_toggle' ) );
		add_filter( 'plugin_action_links_' . plugin_basename( __FILE__ ), array( $this, 'action_links' ) );
		// v1.2: background refresh, from GitHub's call and from WordPress's own schedule.
		add_action( 'rest_api_init', array( $this, 'rest_routes' ) );
		add_filter( 'cron_schedules', array( $this, 'cron_schedules' ) );
		add_action( 'init', array( $this, 'ensure_schedule' ) );
		add_action( 'pn_live_refresh_event', array( $this, 'cron_refresh' ) );
		// v1.3: the sitewide Additional CSS from GitHub.
		add_filter( 'wp_get_custom_css', array( $this, 'filter_custom_css' ), 20, 2 );
		add_action( 'admin_post_pn_live_css_reset', array( $this, 'handle_css_reset' ) );
	}

	/* ------------------------------------------------------------------ */
	/* Rendering                                                           */
	/* ------------------------------------------------------------------ */

	private function enabled() {
		if ( '0' === (string) get_option( self::OPT . 'enabled', '1' ) ) {
			return false;
		}
		if ( is_admin() || wp_doing_ajax() || ( defined( 'REST_REQUEST' ) && REST_REQUEST ) ) {
			return false;
		}
		// Keep the pasted code inside the Elementor editor and its preview.
		if ( isset( $_GET['elementor-preview'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
			return false;
		}
		// An administrator can view the pasted version with ?pn-live=off.
		if ( isset( $_GET['pn-live'] ) && 'off' === $_GET['pn-live'] && current_user_can( 'manage_options' ) ) { // phpcs:ignore WordPress.Security.NonceVerification
			return false;
		}
		return true;
	}

	/**
	 * Elementor: swap the content of a Custom HTML widget.
	 *
	 * @param string $content Rendered widget content.
	 * @param object $widget  Elementor widget.
	 * @return string
	 */
	public function filter_widget( $content, $widget ) {
		if ( ! is_object( $widget ) || ! method_exists( $widget, 'get_name' ) || 'html' !== $widget->get_name() ) {
			return $content;
		}
		return $this->swap( $content );
	}

	/**
	 * Elementor element caching would keep an old copy of a live widget for hours; mark live widgets as dynamic.
	 *
	 * @param bool  $dynamic  Elementor's decision.
	 * @param array $raw_data Element data.
	 * @return bool
	 */
	public function not_cached( $dynamic, $raw_data = array() ) {
		if ( is_array( $raw_data ) && isset( $raw_data['widgetType'] ) && 'html' === $raw_data['widgetType'] && isset( $raw_data['settings']['html'] ) && is_string( $raw_data['settings']['html'] ) && false !== strpos( $raw_data['settings']['html'], 'id="pn-' ) ) {
			return true;
		}
		return $dynamic;
	}

	/**
	 * Block editor: swap the content of a Custom HTML block.
	 *
	 * @param string $html  Rendered block.
	 * @param array  $block Block data.
	 * @return string
	 */
	public function filter_block( $html, $block ) {
		if ( ! is_array( $block ) || empty( $block['blockName'] ) || 'core/html' !== $block['blockName'] ) {
			return $html;
		}
		return $this->swap( $html );
	}

	/**
	 * [pn_live id="pn-bp-kenya"] places a live page anywhere shortcodes run.
	 *
	 * @param array $atts Attributes.
	 * @return string
	 */
	public function shortcode( $atts ) {
		$atts = shortcode_atts( array( 'id' => '' ), $atts, 'pn_live' );
		$id   = $this->clean_key( $atts['id'] );
		if ( '' === $id || ! $this->enabled() ) {
			return '';
		}
		$live = $this->live_code( $id );
		return null === $live ? '' : $live;
	}

	/**
	 * Replace pasted code with the live code when its root id is listed in the manifest.
	 *
	 * @param string $content Pasted code.
	 * @return string
	 */
	private function swap( $content ) {
		if ( ! is_string( $content ) || false === strpos( $content, 'pn-' ) || ! $this->enabled() ) {
			return $content;
		}
		if ( ! preg_match_all( '/\bid\s*=\s*["\'](pn-[a-z0-9-]{1,60})["\']/i', $content, $m ) ) {
			return $content;
		}
		$manifest = $this->manifest();
		if ( empty( $manifest['pages'] ) ) {
			return $content;
		}
		$slug = $this->current_slug();
		foreach ( array_unique( $m[1] ) as $id ) {
			$id   = strtolower( $id );
			$keys = '' !== $slug ? array( $id . '@' . $slug, $id ) : array( $id );
			foreach ( $keys as $key ) {
				if ( isset( $manifest['pages'][ $key ] ) ) {
					$live = $this->live_code( $key );
					return null !== $live ? $live : $content;
				}
			}
		}
		return $content;
	}

	/**
	 * The live code for one root id, or null.
	 *
	 * @param string $id Root id.
	 * @return string|null
	 */
	private function live_code( $id ) {
		$manifest = $this->manifest();
		if ( empty( $manifest['pages'][ $id ]['file'] ) ) {
			return null;
		}
		$file = (string) $manifest['pages'][ $id ]['file'];
		if ( ! preg_match( '#^pages/[a-z0-9][a-z0-9-]{0,80}\.html$#', $file ) ) {
			return null;
		}
		$root = strtok( $id, '@' );
		$code = $this->get_file( $file, function ( $body ) use ( $root ) {
			return false !== stripos( $body, 'id="' . $root . '"' ) && false === strpos( $body, '<?php' );
		} );
		if ( null === $code ) {
			return null;
		}
		$version = isset( $manifest['pages'][ $id ]['version'] ) ? preg_replace( '/[^0-9A-Za-z.\-]/', '', (string) $manifest['pages'][ $id ]['version'] ) : '';
		$this->served[ $id ] = true;
		// v1.2: the page cache keeps a served page for a week; refresh() clears it as soon as its code changes.
		$is_404    = function_exists( 'is_404' ) && is_404();
		$is_search = function_exists( 'is_search' ) && is_search();
		if ( ! $is_404 && ! $is_search ) {
			do_action( 'litespeed_control_set_ttl', self::PAGE_TTL );
		}
		return "\n<!-- pn-live: " . esc_html( $id ) . ( $version ? ' v' . esc_html( $version ) : '' ) . " -->\n" . $code;
	}

	/* ------------------------------------------------------------------ */
	/* Fetching                                                            */
	/* ------------------------------------------------------------------ */

	private function repo() {
		return defined( 'PN_LIVE_REPO' ) ? PN_LIVE_REPO : self::REPO;
	}

	private function branch() {
		return defined( 'PN_LIVE_BRANCH' ) ? PN_LIVE_BRANCH : self::BRANCH;
	}

	/**
	 * Where a file is read from: a branch name, or (v1.2) one exact commit, which no cache can hold back.
	 *
	 * @param string      $path Path in the repository.
	 * @param string|null $ref  Commit or branch; the branch when empty.
	 * @return array
	 */
	private function sources( $path, $ref = null ) {
		$repo = $this->repo();
		$ref  = ( is_string( $ref ) && preg_match( '/^[0-9a-f]{40}$|^[A-Za-z0-9._\/-]{1,100}$/', $ref ) ) ? $ref : $this->branch();
		return array(
			'https://raw.githubusercontent.com/' . $repo . '/' . $ref . '/' . $path,
			'https://cdn.jsdelivr.net/gh/' . $repo . '@' . $ref . '/' . $path,
		);
	}

	private function manifest() {
		if ( null !== $this->manifest ) {
			return $this->manifest;
		}
		$raw  = $this->get_file( self::MANIFEST, function ( $body ) {
			$d = json_decode( $body, true );
			return is_array( $d ) && isset( $d['pages'] ) && is_array( $d['pages'] );
		} );
		$data = null === $raw ? null : json_decode( $raw, true );
		$out  = array( 'pages' => array() );
		if ( is_array( $data ) && ! empty( $data['pages'] ) && is_array( $data['pages'] ) ) {
			foreach ( $data['pages'] as $id => $row ) {
				$cid = $this->clean_key( $id );
				if ( '' !== $cid && is_array( $row ) && ! empty( $row['file'] ) ) {
					$out['pages'][ $cid ] = $row;
				}
			}
			$out['redirects'] = array();
			if ( ! empty( $data['redirects'] ) && is_array( $data['redirects'] ) ) {
				foreach ( $data['redirects'] as $from => $to ) {
					$from = $this->clean_path( $from );
					$to   = $this->clean_path( $to );
					if ( '' !== $from && '' !== $to && $from !== $to ) {
						$out['redirects'][ $from ] = $to;
					}
				}
			}
			$out['updated'] = isset( $data['updated'] ) ? (string) $data['updated'] : '';
			$out['css']     = '';
			if ( ! empty( $data['additional_css']['file'] ) && is_string( $data['additional_css']['file'] ) && preg_match( '#^pages/[a-z0-9][a-z0-9-]{0,80}\.css$#', $data['additional_css']['file'] ) ) {
				$out['css']         = $data['additional_css']['file'];
				$out['css_version'] = isset( $data['additional_css']['version'] ) ? preg_replace( '/[^0-9A-Za-z.\-]/', '', (string) $data['additional_css']['version'] ) : '';
			}
		}
		$this->manifest = $out;
		return $out;
	}

	/**
	 * A repository file. v1.2: the stored copy is served at once, so a visitor never waits for GitHub;
	 * refresh() keeps it current in the background. Only a file never fetched before is read now.
	 *
	 * @param string   $path  Path in the repository.
	 * @param callable $valid Check on the body.
	 * @return string|null
	 */
	private function get_file( $path, $valid ) {
		$key  = substr( md5( $path ), 0, 16 );
		$last = get_option( self::OPT . 'l_' . $key, null );
		if ( is_string( $last ) && '' !== $last ) {
			return call_user_func( $valid, $last ) ? $last : null;
		}
		if ( get_transient( self::OPT . 'x_' . $key ) ) {
			return null;
		}
		if ( 'failed' === $this->fetch_into( $path, null, $valid ) ) {
			set_transient( self::OPT . 'x_' . $key, 1, self::RETRY );
			return null;
		}
		$body = get_option( self::OPT . 'l_' . $key, null );
		return ( is_string( $body ) && '' !== $body ) ? $body : null;
	}

	/**
	 * Read one file from GitHub into its stored copy.
	 *
	 * @param string      $path  Path in the repository.
	 * @param string|null $ref   Commit or branch.
	 * @param callable    $valid Check on the body.
	 * @return string 'changed', 'same' or 'failed'.
	 */
	private function fetch_into( $path, $ref, $valid ) {
		$key   = substr( md5( $path ), 0, 16 );
		$have  = get_option( self::OPT . 'l_' . $key, null );
		$have  = ( is_string( $have ) && '' !== $have ) ? $have : null;
		$meta  = get_option( self::OPT . 'meta', array() );
		$meta  = is_array( $meta ) ? $meta : array();
		$files = ( isset( $meta['files'] ) && is_array( $meta['files'] ) ) ? $meta['files'] : array();
		$etag  = ( null !== $have && isset( $files[ $path ]['etag'] ) ) ? (string) $files[ $path ]['etag'] : '';
		foreach ( $this->sources( $path, $ref ) as $url ) {
			$headers = array( 'Accept' => 'text/plain, text/html, application/json' );
			if ( '' !== $etag ) {
				$headers['If-None-Match'] = $etag;
			}
			$res = wp_remote_get( $url, array(
				'timeout'     => 8,
				'redirection' => 2,
				'headers'     => $headers,
			) );
			if ( is_wp_error( $res ) ) {
				continue;
			}
			$code = (int) wp_remote_retrieve_response_code( $res );
			if ( 304 === $code && null !== $have ) {
				return 'same';
			}
			if ( 200 !== $code ) {
				continue;
			}
			$body = (string) wp_remote_retrieve_body( $res );
			if ( '' === $body || strlen( $body ) > self::MAX || ! call_user_func( $valid, $body ) ) {
				continue;
			}
			$host = (string) wp_parse_url( $url, PHP_URL_HOST );
			$files[ $path ] = array(
				'etag'  => 0 === strpos( $host, 'raw.' ) ? (string) wp_remote_retrieve_header( $res, 'etag' ) : '',
				'md5'   => md5( $body ),
				'time'  => time(),
				'bytes' => strlen( $body ),
			);
			$meta['files'] = $files;
			update_option( self::OPT . 'meta', $meta, false );
			$log          = get_option( self::OPT . 'log', array() );
			$log          = is_array( $log ) ? $log : array();
			$log[ $path ] = array( 'time' => time(), 'from' => $host, 'bytes' => strlen( $body ) );
			update_option( self::OPT . 'log', $log, false );
			if ( null !== $have && md5( $have ) === md5( $body ) ) {
				return 'same';
			}
			update_option( self::OPT . 'l_' . $key, $body, false );
			return 'changed';
		}
		return 'failed';
	}

	/**
	 * main's latest commit, read from github.com itself (never from a cache), or null.
	 *
	 * @return string|null
	 */
	private function main_sha() {
		$res = wp_remote_get( 'https://github.com/' . $this->repo() . '.git/info/refs?service=git-upload-pack', array(
			'timeout'     => 8,
			'redirection' => 3,
		) );
		if ( is_wp_error( $res ) || 200 !== (int) wp_remote_retrieve_response_code( $res ) ) {
			return null;
		}
		$body = (string) wp_remote_retrieve_body( $res );
		if ( preg_match( '#([0-9a-f]{40}) refs/heads/' . preg_quote( $this->branch(), '#' ) . '(?:\x00|\n|$)#', $body, $m ) ) {
			return $m[1];
		}
		return null;
	}

	/**
	 * Bring every stored copy up to date with GitHub; clear the page cache once if any file changed.
	 *
	 * @param bool $force Read every file even when main has not moved.
	 * @param bool $light Only note that main moved (the hourly safety net decides when to read the files).
	 * @return array
	 */
	public function refresh( $force = false, $light = false ) {
		if ( ! $force && get_transient( self::OPT . 'lock' ) ) {
			return array( 'status' => 'busy' );
		}
		set_transient( self::OPT . 'lock', 1, 300 );
		$this->refreshing = true;
		if ( function_exists( 'set_time_limit' ) ) {
			@set_time_limit( 300 ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
		}
		$sha  = $this->main_sha();
		$meta = get_option( self::OPT . 'meta', array() );
		$meta = is_array( $meta ) ? $meta : array();
		if ( ! $force && null !== $sha && isset( $meta['sha'] ) && $meta['sha'] === $sha ) {
			$meta['checked'] = time();
			update_option( self::OPT . 'meta', $meta, false );
			delete_transient( self::OPT . 'lock' );
			$this->refreshing = false;
			return array( 'status' => 'unchanged', 'sha' => $sha );
		}
		if ( $light && ! $force ) {
			$meta['checked'] = time();
			update_option( self::OPT . 'meta', $meta, false );
			delete_transient( self::OPT . 'lock' );
			$this->refreshing = false;
			return array( 'status' => 'deferred', 'sha' => $sha );
		}
		$changed = array();
		$failed  = array();
		$r = $this->fetch_into( self::MANIFEST, $sha, function ( $body ) {
			$d = json_decode( $body, true );
			return is_array( $d ) && isset( $d['pages'] ) && is_array( $d['pages'] );
		} );
		if ( 'changed' === $r ) {
			$changed[] = self::MANIFEST;
		} elseif ( 'failed' === $r ) {
			$failed[] = self::MANIFEST;
		}
		$this->manifest = null;
		$manifest       = $this->manifest();
		$roots          = array();
		foreach ( ( isset( $manifest['pages'] ) ? $manifest['pages'] : array() ) as $id => $row ) {
			$file = isset( $row['file'] ) ? (string) $row['file'] : '';
			if ( preg_match( '#^pages/[a-z0-9][a-z0-9-]{0,80}\.html$#', $file ) ) {
				$roots[ $file ][] = strtok( $id, '@' );
			}
		}
		foreach ( $roots as $file => $ids ) {
			$ids = array_values( array_unique( $ids ) );
			$r   = $this->fetch_into( $file, $sha, function ( $body ) use ( $ids ) {
				if ( false !== strpos( $body, '<?php' ) ) {
					return false;
				}
				foreach ( $ids as $root ) {
					if ( false !== stripos( $body, 'id="' . $root . '"' ) ) {
						return true;
					}
				}
				return false;
			} );
			if ( 'changed' === $r ) {
				$changed[] = $file;
			} elseif ( 'failed' === $r ) {
				$failed[] = $file;
			}
		}
		if ( ! empty( $manifest['css'] ) ) {
			$r = $this->fetch_into( $manifest['css'], $sha, array( $this, 'valid_css' ) );
			if ( 'changed' === $r ) {
				$changed[] = $manifest['css'];
			} elseif ( 'failed' === $r ) {
				$failed[] = $manifest['css'];
			}
		}
		$meta            = get_option( self::OPT . 'meta', array() );
		$meta            = is_array( $meta ) ? $meta : array();
		$meta['checked'] = time();
		$meta['full']    = time();
		if ( null !== $sha && empty( $failed ) ) {
			$meta['sha'] = $sha;
		}
		if ( ! empty( $changed ) ) {
			$meta['changed'] = time();
		}
		update_option( self::OPT . 'meta', $meta, false );
		if ( ! empty( $changed ) ) {
			do_action( 'litespeed_purge_all' );
		}
		delete_transient( self::OPT . 'lock' );
		$this->refreshing = false;
		return array(
			'status'  => empty( $changed ) ? 'unchanged' : 'updated',
			'sha'     => $sha,
			'changed' => $changed,
			'failed'  => $failed,
		);
	}

	/**
	 * v1.3: serve pages/additional.css in place of Appearance > Customize > Additional CSS.
	 *
	 * @param string $css        The Additional CSS kept in WordPress.
	 * @param string $stylesheet Theme.
	 * @return string
	 */
	public function filter_custom_css( $css, $stylesheet = '' ) {
		if ( ! $this->enabled() || ( function_exists( 'is_customize_preview' ) && is_customize_preview() ) ) {
			return $css;
		}
		$manifest = $this->manifest();
		if ( empty( $manifest['css'] ) ) {
			return $css;
		}
		$now  = md5( (string) $css );
		$base = (string) get_option( self::OPT . 'css_base', '' );
		if ( '' === $base ) {
			update_option( self::OPT . 'css_base', $now, false );
			$base = $now;
		}
		if ( $base !== $now ) {
			return $css; // edited in WordPress after the switch: the edit wins
		}
		$live = $this->get_file( $manifest['css'], array( $this, 'valid_css' ) );
		return ( is_string( $live ) && '' !== $live ) ? $live : $css;
	}

	/** A sitewide stylesheet from the repository: marked as ours, no markup, a sane size. */
	public function valid_css( $body ) {
		$body = (string) $body;
		return 0 === strpos( ltrim( $body ), '/* Perfect Nations' ) && false === strpos( $body, '<' ) && strlen( $body ) < 400000;
	}

	public function handle_css_reset() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Not allowed.' );
		}
		check_admin_referer( 'pn_live_css_reset' );
		delete_option( self::OPT . 'css_base' );
		do_action( 'litespeed_purge_all' );
		wp_safe_redirect( admin_url( 'options-general.php?page=pn-live&pn-done=css' ) );
		exit;
	}

	/* WordPress's own schedule: a check every ten minutes, whenever the site runs. */
	public function cron_schedules( $schedules ) {
		$schedules['pn_live_ten'] = array(
			'interval' => self::TTL,
			'display'  => 'Every ten minutes (Perfect Nations Live)',
		);
		return $schedules;
	}

	public function ensure_schedule() {
		if ( function_exists( 'wp_next_scheduled' ) && ! wp_next_scheduled( 'pn_live_refresh_event' ) ) {
			wp_schedule_event( time() + 60, 'pn_live_ten', 'pn_live_refresh_event' );
		}
	}

	/* The schedule is the safety net: GitHub's call does the prompt work, so the schedule reads the files at most once an hour. */
	public function cron_refresh() {
		if ( '0' === (string) get_option( self::OPT . 'enabled', '1' ) ) {
			return;
		}
		$meta = get_option( self::OPT . 'meta', array() );
		$full = ( is_array( $meta ) && isset( $meta['full'] ) ) ? (int) $meta['full'] : 0;
		$this->refresh( false, ( time() - $full ) < 3600 );
	}

	/* GitHub's call after a change to main. Open to anyone, but it can only start a check, at most once a minute. */
	public function rest_routes() {
		register_rest_route( 'pn-live/v1', '/refresh', array(
			'methods'             => 'POST',
			'permission_callback' => '__return_true',
			'callback'            => array( $this, 'rest_refresh' ),
		) );
	}

	public function rest_refresh() {
		if ( '0' === (string) get_option( self::OPT . 'enabled', '1' ) ) {
			return new WP_REST_Response( array( 'status' => 'off' ), 200 );
		}
		if ( get_transient( self::OPT . 'ping' ) ) {
			return new WP_REST_Response( array( 'status' => 'wait' ), 429 );
		}
		set_transient( self::OPT . 'ping', 1, self::PING_GAP );
		return new WP_REST_Response( $this->refresh( false ), 200 );
	}

	private function clean_id( $id ) {
		$id = strtolower( trim( (string) $id ) );
		return preg_match( '/^pn-[a-z0-9-]{1,60}$/', $id ) ? $id : '';
	}

	/** A manifest key: a root id, or a root id and one post slug ("pn-disp@post-slug"). */
	private function clean_key( $key ) {
		$key = strtolower( trim( (string) $key ) );
		return preg_match( '/^pn-[a-z0-9-]{1,60}(@[a-z0-9_-]{1,190})?$/', $key ) ? $key : '';
	}

	/** A same-site path such as "/dear-zimbabwe/". */
	private function clean_path( $path ) {
		$path = strtolower( trim( (string) $path ) );
		return preg_match( '#^/[a-z0-9/_-]{0,200}$#', $path ) ? $path : '';
	}

	/** The slug of the post being shown, if any. */
	private function current_slug() {
		$post = function_exists( 'get_post' ) ? get_post() : null;
		if ( ! $post && function_exists( 'get_queried_object' ) ) {
			$post = get_queried_object();
		}
		return ( is_object( $post ) && ! empty( $post->post_name ) ) ? strtolower( (string) $post->post_name ) : '';
	}

	/** Same-site 301 redirects listed in the manifest (for example a duplicate post). */
	public function redirects() {
		if ( is_admin() || '0' === (string) get_option( self::OPT . 'enabled', '1' ) ) {
			return;
		}
		$manifest = $this->manifest();
		if ( empty( $manifest['redirects'] ) ) {
			return;
		}
		$path = isset( $_SERVER['REQUEST_URI'] ) ? strtolower( (string) wp_parse_url( wp_unslash( $_SERVER['REQUEST_URI'] ), PHP_URL_PATH ) ) : ''; // phpcs:ignore
		$path = '/' . trim( $path, '/' ) . '/';
		if ( isset( $manifest['redirects'][ $path ] ) ) {
			wp_safe_redirect( home_url( $manifest['redirects'][ $path ] ), 301 );
			exit;
		}
	}

	private function forget_all() {
		global $wpdb;
		// Fresh copies and failure markers only; the last good copies stay as the safety net.
		$like1 = $wpdb->esc_like( '_transient_' . self::OPT . 'f_' ) . '%';
		$like2 = $wpdb->esc_like( '_transient_' . self::OPT . 'x_' ) . '%';
		$names = $wpdb->get_col( $wpdb->prepare( "SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s", $like1, $like2 ) ); // phpcs:ignore WordPress.DB.DirectDatabaseQuery
		foreach ( (array) $names as $name ) {
			delete_transient( substr( $name, strlen( '_transient_' ) ) );
		}
		$this->manifest = null;
	}

	/* ------------------------------------------------------------------ */
	/* Admin                                                               */
	/* ------------------------------------------------------------------ */

	public function action_links( $links ) {
		array_unshift( $links, '<a href="' . esc_url( admin_url( 'options-general.php?page=pn-live' ) ) . '">' . esc_html__( 'Settings', 'pn-live' ) . '</a>' );
		return $links;
	}

	public function admin_menu() {
		add_options_page( 'Perfect Nations Live', 'Perfect Nations Live', 'manage_options', 'pn-live', array( $this, 'admin_page' ) );
	}

	public function admin_page() {
		if ( ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$manifest = $this->manifest();
		$log      = get_option( self::OPT . 'log', array() );
		$on       = '0' !== (string) get_option( self::OPT . 'enabled', '1' );
		$notice   = isset( $_GET['pn-done'] ) ? sanitize_key( wp_unslash( $_GET['pn-done'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification
		echo '<div class="wrap"><h1>Perfect Nations Live Pages</h1>';
		if ( 'refreshed' === $notice ) {
			echo '<div class="notice notice-success"><p>Refreshed. Every live page has been fetched again from GitHub and the page cache has been cleared.</p></div>';
		} elseif ( 'css' === $notice ) {
			echo '<div class="notice notice-success"><p>The Additional CSS from GitHub is served again.</p></div>';
		} elseif ( 'toggled' === $notice ) {
			echo '<div class="notice notice-success"><p>Saved.</p></div>';
		}
		echo '<p>Pages listed below are served from the GitHub repository <code>' . esc_html( self::REPO ) . '</code> (branch <code>' . esc_html( self::BRANCH ) . '</code>), in place of the code pasted in their Elementor widget. A change merged into GitHub reaches the site within about a minute (GitHub tells the site; the site also checks by itself every ten minutes), or at once with Refresh now. Pages stay in the page cache until their code changes, so visitors never wait for GitHub.</p>';
		$meta = get_option( self::OPT . 'meta', array() );
		if ( is_array( $meta ) && ! empty( $meta['checked'] ) ) {
			echo '<p><strong>Last check:</strong> ' . esc_html( human_time_diff( (int) $meta['checked'] ) ) . ' ago' . ( ! empty( $meta['sha'] ) ? ', at commit <code>' . esc_html( substr( (string) $meta['sha'], 0, 7 ) ) . '</code>' : '' ) . ( ! empty( $meta['changed'] ) ? '. Last change: ' . esc_html( human_time_diff( (int) $meta['changed'] ) ) . ' ago.' : '.' ) . '</p>';
		}

		echo '<p><strong>Status:</strong> ' . ( $on ? 'Live pages are on.' : 'Live pages are off: every page shows its pasted code.' ) . '</p>';
		if ( ! empty( $manifest['css'] ) ) {
			$wp_css = function_exists( 'wp_get_custom_css_post' ) ? wp_get_custom_css_post() : null;
			$wp_raw = ( is_object( $wp_css ) && isset( $wp_css->post_content ) ) ? (string) $wp_css->post_content : '';
			$base   = (string) get_option( self::OPT . 'css_base', '' );
			$paused = '' !== $base && md5( $wp_raw ) !== $base;
			$copy   = get_option( self::OPT . 'l_' . substr( md5( $manifest['css'] ), 0, 16 ), '' );
			echo '<p><strong>Additional CSS:</strong> ' . ( $paused
				? 'paused. The Additional CSS in Appearance &gt; Customize was edited after the switch, so the WordPress copy is served.'
				: 'served from GitHub (<code>' . esc_html( $manifest['css'] ) . '</code>' . ( ! empty( $manifest['css_version'] ) ? ' v' . esc_html( $manifest['css_version'] ) : '' ) . ', ' . esc_html( (string) round( strlen( (string) $copy ) / 1024 ) ) . ' KB) in place of the ' . esc_html( (string) round( strlen( $wp_raw ) / 1024 ) ) . ' KB kept in Appearance &gt; Customize, which stays as the fallback.' ) . '</p>';
			if ( $paused ) {
				echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="margin:0 0 16px 0">';
				wp_nonce_field( 'pn_live_css_reset' );
				echo '<input type="hidden" name="action" value="pn_live_css_reset"><button class="button">Use the GitHub copy again</button></form>';
			}
		}

		echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="display:inline-block;margin:0 8px 16px 0">';
		wp_nonce_field( 'pn_live_refresh' );
		echo '<input type="hidden" name="action" value="pn_live_refresh"><button class="button button-primary">Refresh now</button></form>';

		echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="display:inline-block;margin:0 8px 16px 0">';
		wp_nonce_field( 'pn_live_export' );
		echo '<input type="hidden" name="action" value="pn_live_export"><button class="button">Export page code</button></form>';

		echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '" style="display:inline-block;margin:0 0 16px 0">';
		wp_nonce_field( 'pn_live_toggle' );
		echo '<input type="hidden" name="action" value="pn_live_toggle"><button class="button">' . ( $on ? 'Turn live pages off' : 'Turn live pages on' ) . '</button></form>';

		echo '<h2>Live pages</h2>';
		if ( empty( $manifest['pages'] ) ) {
			echo '<p>The page list could not be read from GitHub yet. Press Refresh now; if it stays empty, the site may not be able to reach raw.githubusercontent.com.</p>';
		} else {
			echo '<table class="widefat striped" style="max-width:980px"><thead><tr><th>Root id</th><th>Page</th><th>Version</th><th>File</th><th>Last fetched</th></tr></thead><tbody>';
			foreach ( $manifest['pages'] as $id => $row ) {
				$file = isset( $row['file'] ) ? (string) $row['file'] : '';
				$when = ( is_array( $log ) && isset( $log[ $file ]['time'] ) ) ? human_time_diff( (int) $log[ $file ]['time'] ) . ' ago' : 'Not yet (fetched at the next check)';
				echo '<tr><td><code>' . esc_html( $id ) . '</code></td><td>' . esc_html( isset( $row['title'] ) ? $row['title'] : '' ) . '</td><td>' . esc_html( isset( $row['version'] ) ? $row['version'] : '' ) . '</td><td><code>' . esc_html( $file ) . '</code></td><td>' . esc_html( $when ) . '</td></tr>';
			}
			echo '</tbody></table>';
			if ( ! empty( $manifest['redirects'] ) ) {
				echo '<h2>Redirects</h2><ul>';
				foreach ( $manifest['redirects'] as $from => $to ) {
					echo '<li><code>' . esc_html( $from ) . '</code> &rarr; <code>' . esc_html( $to ) . '</code></li>';
				}
				echo '</ul>';
			}
			if ( ! empty( $manifest['updated'] ) ) {
				echo '<p>Page list updated ' . esc_html( $manifest['updated'] ) . '.</p>';
			}
		}
		echo '<h2>Export page code</h2><p>Downloads one file with the code pasted in every Perfect Nations widget on the site (every Custom HTML widget whose code has a root id beginning <code>pn-</code>). Upload that file in the Claude conversation, and every page can be updated in GitHub at once.</p>';
		echo '<h2>To see the pasted version</h2><p>While signed in as an administrator, add <code>?pn-live=off</code> to any page address.</p>';
		echo '</div>';
	}

	public function handle_refresh() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Not allowed.' );
		}
		check_admin_referer( 'pn_live_refresh' );
		$this->forget_all();
		$this->refresh( true );
		do_action( 'litespeed_purge_all' );
		if ( class_exists( '\\Elementor\\Plugin' ) && isset( \Elementor\Plugin::$instance->files_manager ) ) {
			\Elementor\Plugin::$instance->files_manager->clear_cache();
		}
		if ( function_exists( 'rocket_clean_domain' ) ) {
			rocket_clean_domain();
		}
		wp_safe_redirect( admin_url( 'options-general.php?page=pn-live&pn-done=refreshed' ) );
		exit;
	}

	public function handle_toggle() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Not allowed.' );
		}
		check_admin_referer( 'pn_live_toggle' );
		$on = '0' !== (string) get_option( self::OPT . 'enabled', '1' );
		update_option( self::OPT . 'enabled', $on ? '0' : '1', true );
		do_action( 'litespeed_purge_all' );
		wp_safe_redirect( admin_url( 'options-general.php?page=pn-live&pn-done=toggled' ) );
		exit;
	}

	public function handle_export() {
		if ( ! current_user_can( 'manage_options' ) ) {
			wp_die( 'Not allowed.' );
		}
		check_admin_referer( 'pn_live_export' );
		$out   = array();
		$posts = get_posts( array(
			'post_type'      => array( 'page', 'post', 'elementor_library' ),
			'post_status'    => array( 'publish', 'draft', 'private', 'pending', 'future' ),
			'posts_per_page' => -1,
			'fields'         => 'ids',
			'no_found_rows'  => true,
		) );
		foreach ( $posts as $pid ) {
			$codes = array();
			$raw   = get_post_meta( $pid, '_elementor_data', true );
			if ( is_string( $raw ) && '' !== $raw ) {
				$tree = json_decode( $raw, true );
				$this->collect( $tree, $codes );
			} elseif ( is_array( $raw ) ) {
				$this->collect( $raw, $codes );
			}
			$content = (string) get_post_field( 'post_content', $pid );
			if ( empty( $codes ) && false !== strpos( $content, 'id="pn-' ) ) {
				$codes[] = $content;
			}
			foreach ( $codes as $code ) {
				if ( ! preg_match( '/\bid\s*=\s*["\'](pn-[a-z0-9-]{1,60})["\']/i', $code, $m ) ) {
					continue;
				}
				$out[] = array(
					'post_id'   => (int) $pid,
					'post_type' => get_post_type( $pid ),
					'status'    => get_post_status( $pid ),
					'title'     => get_the_title( $pid ),
					'slug'      => get_post_field( 'post_name', $pid ),
					'url'       => get_permalink( $pid ),
					'modified'  => get_post_modified_time( 'c', true, $pid ),
					'root'      => strtolower( $m[1] ),
					'header'    => substr( trim( strtok( $code, "\n" ) ), 0, 300 ),
					'bytes'     => strlen( $code ),
					'code'      => $code,
				);
			}
		}
		$body = wp_json_encode( array(
			'site'     => home_url( '/' ),
			'exported' => gmdate( 'c' ),
			'plugin'   => self::VERSION,
			'count'    => count( $out ),
			'widgets'  => $out,
		), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES );
		nocache_headers();
		header( 'Content-Type: application/json; charset=utf-8' );
		header( 'Content-Disposition: attachment; filename="pn-pages-export-' . gmdate( 'Y-m-d' ) . '.json"' );
		echo $body; // phpcs:ignore WordPress.Security.EscapeOutput
		exit;
	}

	/**
	 * Every Custom HTML widget's code in an Elementor element tree.
	 *
	 * @param mixed $elements Elements.
	 * @param array $codes    Collected code.
	 */
	private function collect( $elements, &$codes ) {
		if ( ! is_array( $elements ) ) {
			return;
		}
		foreach ( $elements as $el ) {
			if ( ! is_array( $el ) ) {
				continue;
			}
			if ( isset( $el['elType'], $el['widgetType'] ) && 'widget' === $el['elType'] && 'html' === $el['widgetType'] && ! empty( $el['settings']['html'] ) && is_string( $el['settings']['html'] ) ) {
				$codes[] = $el['settings']['html'];
			}
			if ( ! empty( $el['elements'] ) ) {
				$this->collect( $el['elements'], $codes );
			}
		}
	}
}

PN_Live_Pages::instance();

register_deactivation_hook( __FILE__, function () {
	wp_clear_scheduled_hook( 'pn_live_refresh_event' );
} );
