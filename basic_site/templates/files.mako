<%include file="head.mako" />

<DIV id="main">
  <FORM method="POST" action="${request.route_url('files')}"
        enctype="multipart/form-data">
    <INPUT type="file" name="data">
    <BUTTON type="submit">Submit File</BUTTON>
  <FORM>

</DIV>

<%include file="foot.mako" />
