<%include file="head.mako" />

<DIV id="main">

% if user.admin:
  <DIV id="add_user">
    <H3>Add User:</H3>
    <FORM method="POST" action="${request.route_url('users')}">
      <LABEL for="uid">User Name:</LABEL>
      <INPUT type="text" maxlength="10" size="10" name="uid">
      <LABEL for="fullname">Full Name:</LABEL>
      <INPUT type="text" size="30" name="fullname">
      <LABEL for="passwd">Password:</LABEL>
      <INPUT type="password" size="20" name="passwd">
      <LABEL for="repeat">Password (again):</LABEL>
      <INPUT type="password" size="20" name="repeat">
      <LABEL for="admin">Admin:</LABEL>
      <INPUT type="checkbox" name="admin"> 
      <BUTTON type="submit" name="action" value="add">Add User</BUTTON>
    </FORM>
  </DIV>
%endif

<DIV id="change_pw">
  <H3>Change your password:</H3>
  <FORM method="POST" action="${request.route_url('users')}">
    <LABEL for="old">Current Password:</LABEL>
    <INPUT type="password" size="20" name="old">
    <LABEL for="passwd">New Password:</LABEL>
    <INPUT type="password" size="20" name="new">
    <LABEL for="repeat">New Password (again):</LABEL>
    <INPUT type="password" size="20" name="repeat">
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

</DIV>

<%include file="foot.mako" />
