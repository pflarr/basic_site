<%include file="head.mako" />

<DIV class="content">
  <H2>${post.title}</H2>    
  ${post.render()|n}
  <DIV class="page_footer">
    <SPAN class="creator">${post.creator|h}</SPAN>
    <SPAN class="created">${post.created|h}</SPAN>
  </DIV>
</DIV>

<%include file="foot.mako" />
