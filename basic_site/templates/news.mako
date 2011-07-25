<%include file="head.mako" />

<DIV id="main">
% for item in news:
  <DIV class="news">
    ${item.content}
    <DIV class="news_footer">
      <SPAN class="creator">${item.creator|h}</SPAN>
      <SPAN class="created">${item.created|h}</SPAN>
    </DIV>
  </DIV>
% endfor
</DIV>

<%include file="foot.mako" />
