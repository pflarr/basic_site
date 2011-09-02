<%include file="head.mako" />

<DIV id="main">
% for post in posts:
  <DIV class="news">
    ${post.content}
    <DIV class="news_footer">
      <SPAN class="creator">${post.creator|h}</SPAN>
      <SPAN class="created">${post.created|h}</SPAN>
    </DIV>
  </DIV>
% endfor
</DIV>

<%include file="foot.mako" />
