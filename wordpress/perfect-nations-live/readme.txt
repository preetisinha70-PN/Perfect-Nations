=== Perfect Nations Live Pages ===
Version: 1.3.0
Requires PHP: 7.4

Serves each Perfect Nations page from the Perfect Nations GitHub repository, so a page updates
without copying and pasting its code.

== Install (once) ==
1. WordPress admin > Plugins > Add New Plugin > Upload Plugin. Choose perfect-nations-live.zip,
   press Install Now, then Activate.
2. Settings > Perfect Nations Live: press Refresh now. The table lists every live page.
3. Open the Perfect Capita page, the homepage, State of Nations and the Barbados blueprint: each
   now shows the version in GitHub. Nothing in Elementor changes.

== Every day after ==
Nothing. A page change merged into GitHub appears within about a minute: GitHub tells the site
(the workflow .github/workflows/site-refresh.yml in the repository), and the site also checks by
itself. Refresh now does it at once.

== Export page code ==
Settings > Perfect Nations Live > Export page code downloads one file with the code of every
Perfect Nations widget on the site. Upload it in the Claude conversation so every blueprint can be
moved into GitHub and updated at once.

== Safety ==
- If GitHub cannot be reached, the last good copy is shown; if there is none, the pasted code.
- Only the repository preetisinha70-PN/perfect-nations is read, and only files listed in
  pages/manifest.json whose code contains the expected root id.
- To see the pasted version while signed in as an administrator, add ?pn-live=off to a page address.
- Turn live pages off: Settings > Perfect Nations Live > Turn live pages off (or deactivate the plugin).
- If Elementor > Settings > Performance > Element Caching is active and a page does not update,
  press Refresh now, or set Element Caching to Inactive.

== Update from 1.0 ==
Plugins > Add New Plugin > Upload Plugin, choose the new perfect-nations-live.zip, press Install Now,
then "Replace current with uploaded". Settings stay as they are.

== Changes ==
1.3.0 (7 November 2026) - sitewide CSS
- When pages/manifest.json names {"additional_css": {"file": "pages/additional.css"}}, that file is
  served as the sitewide Additional CSS in place of the copy in Appearance > Customize > Additional CSS.
  The WordPress copy stays untouched as the fallback; if it is edited there after the switch, the
  edited WordPress copy is served until Settings > Perfect Nations Live > Use the GitHub copy again.
- The Customizer preview always shows the WordPress copy. The file is checked with the pages and must
  begin with "/* Perfect Nations" and hold no markup.

1.2.0 (7 November 2026) - speed
- Pages stay in the LiteSpeed page cache for a week, or until their code changes (1.1 told
  LiteSpeed to drop every page after ten minutes, so most visitors waited for a fresh build).
- Visitors are always served the stored copy; no page view waits for GitHub any more.
- The stored copies are refreshed in the background: GitHub calls POST /wp-json/pn-live/v1/refresh
  after each change to pages/ (at most once a minute), and WordPress checks every ten minutes as a
  safety net. A check reads main's commit from github.com; files are read at that exact commit, each
  with its ETag, and the page cache is cleared once only when a file really changed.
- A 404 or search page is not kept for a week.

1.1.0
- A manifest entry can name one post ("pn-disp@post-slug"). Posts that share a root id, such as
  dispatches, can each be served on their own, and a stray widget on one page can be replaced.
- The manifest can list same-site redirects ("redirects"), answered with a 301. Only paths on
  perfectnations.org are accepted.
1.0.0
- First version.
