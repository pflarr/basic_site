<HTML>
<HEAD>
    <TITLE>${request.registry.settings['site_name'] + page_subtitle|h}</TITLE>
    <LINK type="text/css" rel="stylesheet"
          href="${request.static_url('basic_site:static/base.css')}">
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

% if message:
    <DIV class="message">${message|h}</DIV>
% endif
</DIV>

<%
    def cur_class(this_page):
        if this_page == page_name:
            return 'class="current"'
        else:
            return ''
%>
<DIV class=main>
  <DIV class=pages>
    <strong>Navigation:</strong>
    <UL>
      <LI ${cur_class('*Main')|n}>
        <A href="${request.route_url('home')}">Main</A>
    % if user:
      <LI ${cur_class('*Users')|n}>
        <A href="${request.route_url('users')}">Users</A>
      <LI ${cur_class('*Files')|n}>
        <A href="${request.route_url('files')}">Files</A>
    % endif
    % for page in menu_pages:
      <LI><A href="${request.route_url('page', id=page.id)}">grarg</A>
    % endfor
    </UL>

  </DIV>
