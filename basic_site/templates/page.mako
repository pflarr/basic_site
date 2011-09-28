<%include file="head.mako" />

<DIV class="content">
    ${page.render()|n}
    <DIV class="page_footer">
      <SPAN class="creator">${page.creator|h}</SPAN>
      <SPAN class="created">${page.created|h}</SPAN>
    </DIV>
</DIV>

<%include file="foot.mako" />
