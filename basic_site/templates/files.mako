<%include file="head.mako" />

<FORM method="POST" action="${request.route_url('files')}"
      enctype="multipart/form-data">
  <INPUT type="file" name="data">
  <BUTTON type="submit">Submit File</BUTTON>
<FORM>

<%
  names = files.keys()
  names.sort()
%>

<TABLE>
  <TR><TH>Name<TH>Added By<TH>Added
% for name in names:
  % for i in range(len(files[name])):
  <% 
    file = files[name][i]
    href = request.route_url('file_rev', name=file.name, rev=i)
    f_class = 'class=old_file' if i > 0 else ''
  %>
    <TR ${f_class|n}>
      <TD><A href="${href}">${file.name|h}</A>
      <TD>${file.submitter|h}
      <TD>${file.changed.strftime('%Y-%m-%d %H:%M:%S')|h}
  % endfor
% endfor
</TABLE>

<%include file="foot.mako" />
