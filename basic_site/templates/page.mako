<%include file="head.mako" />

<DIV id="main">
    ${page.content}
    <DIV class="page_footer">
      <SPAN class="creator">${page.creator|h}</SPAN>
      <SPAN class="created">${page.created|h}</SPAN>
    </DIV>
% endfor
</DIV>

<%include file="foot.mako" />
