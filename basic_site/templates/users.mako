<%include file="head.mako" />

% if user.admin:
  <DIV class="add_user">
    <H3>Add User:</H3>
    <FORM method="POST" action="${request.route_url('users')}"
          autocomplete="off">
      <INPUT type="text" maxlength="10" size="20" name="uid">
      <LABEL for="uid">User Name</LABEL><BR>
      <INPUT type="text" size="20" name="fullname">
      <LABEL for="fullname">Full Name</LABEL><BR>
      <INPUT type="password" size="20" name="passwd">
      <LABEL for="passwd">Password</LABEL><BR>
      <INPUT type="password" size="20" name="repeat">
      <LABEL for="repeat">Password (again)</LABEL><BR>
      <INPUT type="checkbox" name="admin"> 
      <LABEL for="admin">Admin?</LABEL><BR>
      <BUTTON type="submit" name="action" value="add">Add User</BUTTON>
    </FORM>
  </DIV>
%endif

<DIV id="change_pw">
  <H3>Change your password:</H3>
  <FORM method="POST" action="${request.route_url('users')}"
        autocomplete="off">
    <INPUT type="password" size="20" name="old">
    <LABEL for="old">Current Password</LABEL><BR>
    <INPUT type="password" size="20" name="new">
    <LABEL for="passwd">New Password</LABEL><BR>
    <INPUT type="password" size="20" name="repeat">
    <LABEL for="repeat">New Password (again)</LABEL><BR>
    <BUTTON type="submit" name="action" 
            value="change_pw">Change Password</BUTTON>
  </FORM>
</DIV>

<DIV id="users">
% if user.admin:
  <FORM method="POST" action="${request.route_url('users')}">
% endif
    <TABLE>
      <TR>${'<TH>' if user.admin else ''|n}<TH>User<TH>Full Name<TH>Admin
    % for e_user in users:
      <TR>
      % if user.admin:
        <TD><INPUT type="radio" name="e_uid" value="${e_user.uid}">
      % endif
        <TD>${e_user.uid}<TD>${e_user.fullname}
        <TD>${'yes' if e_user.admin else 'no'}
    % endfor
    % if user.admin:
      <TR><TD colspan=4>For selected user:
      <BUTTON type="submit" name="action" 
              value="toggle_admin">Toggle Admin</BUTTON>
      <BUTTON type="submit" name="action" value="delete">Delete</BUTTON>
    % endif 
    </TABLE>
% if user.admin:
  </FORM>
% endif
</DIV>

<%include file="foot.mako" />
