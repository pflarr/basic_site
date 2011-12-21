<%include file="head.mako" />

<!-- All this whole thing does is redirect you to the appropriate edit          
     post page. -->
<DIV>
    <P>Enter the name of your new page. You'll need to add a post to the page before it will appear.</P>
    <FORM action="${request.route_url('new_page')}" method="GET">
      <LABEL for="page">Page Name:</LABEL>
      <INPUT name="page" type="text" size="15" maxlength="15"
             value="">
      <BUTTON type="submit">Submit</BUTTON>
    </FORM>
</DIV>

<%include file="foot.mako" />
