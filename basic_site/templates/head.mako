<HTML>
<HEAD>
    <TITLE>${request.registry.settings['site_name'] + page.subtitle|h}</TITLE>
    <LINK type="text/css" rel="stylesheet"
          href="${request.static_url(basic_site:static/base.css)}">
</HEAD>
<DIV id="head">
    <IMG src="files/logo.png">
    <DIV id="login">
  % if uid == None:
      <FORM action='' method="POST">
        Login:
        <LABEL target="user">User</LABEL>
        <INPUT type="text" name="user"> 
        <LABEL target="passwd">Password</LABEL>
        <INPUT type="password" name="passwd">
      </FORM>
  % else:
      Logged in as <STRONG>${uid}</STRONG> 
      (<A href="${request.application_url}/logout">logout</A>)
  % endif
    </DIV>
</DIV>

<%
    def cur_class(this_page):
        if this_page == page_name:
            return 'class="current"'
        else:
            return ''
%>
<DIV id=pages>
    <ul>
    <LI><A href="news.cgi" ${cur_class('*Main')}>Main</A>
    <LI><A href="album.cgi" ${cur_class('*Album')}>Album</A>
  % for page in pages:
    <LI><A href="page.cgi?page=${page.name|u}" ${cur_class(page.name)}>${page.name}</A>
  % endfor
</DIV>
