<HTML>
<HEAD>
    <TITLE>${request.registry.settings['site_name'] + page_subtitle|h}</TITLE>
    <LINK type="text/css" rel="stylesheet"
          href="${request.static_url('basic_site:static/base.css')}">
    <LINK type="text/css" rel="stylesheet"
          href="${request.route_url('file', name='theme.css')}">
    <LINK type="text/css" rel="stylesheet"
          href="${request.route_url('file', name='site.css')}">
</HEAD>
<DIV class="head">
    <IMG src="${request.route_url('file',name='logo.png')}">
    <DIV class="login">
  % if user == None:
      <FORM action='' method="POST">
        <LABEL target="user">User</LABEL>
        <INPUT type="text" name="user"> 
        <LABEL target="passwd">Password</LABEL>
        <INPUT type="password" name="passwd">
        <BUTTON type="submit">Login</BUTTON>
      </FORM>
  % else:
      Logged in as <STRONG>${user.uid}</STRONG> 
      (<A href="${request.route_url('logout')}">logout</A>)
  % endif
    </DIV>

</DIV>

% if msg:
  % for item in msg:
    <DIV class="message">${item|h}</DIV>
  % endfor
% endif

<%
    def cur_class(this_page):
        if this_page == page_name:
            return 'class="current"'
        else:
            return ''
%>
<DIV class=main>
  <DIV class=pages>
    <UL>
      <LI ${cur_class('*Main')|n}>
        <A href="${request.route_url('home')}">Main</A>
    % if user:
      <LI ${cur_class('*Users')|n}>
        <A href="${request.route_url('users')}">Users</A>
      <LI ${cur_class('*Files')|n}>
        <A href="${request.route_url('files')}">Files</A>
      <LI ${cur_class('add page')|n}>
        <A href="${request.route_url('add', ptype='page')}"
            >Add New Page</A>
    % endif
    % for page in menu_pages:
      <LI ${cur_class(page.name)|n}>
        <A href="${request.route_url('page', name=page.name)}">${page.name}</A>
    % endfor
    </UL>

  </DIV>
  <DIV class="content">
