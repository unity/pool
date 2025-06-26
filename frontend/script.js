(function w() {
  const container = "navigationPortalContainer";
  const liz = "lizScript";
  var s = document.createElement("script");
  s.id = liz;

  const lizScript = document.getElementById(liz);
  console.log("LIZ");
  console.log(lizScript);
  if (lizScript) {
    return;
  }

  s.dataset.containerId = container;
  s.dataset.theme = "light";
  s.dataset.apiUrl = "http://localhost:8000";
  s.src = "http://localhost:5173/liz-search-widget.js";
  s.type = "module";
  s.onload = function () {
    console.log("LOADED!!!!");
    const lizSearch = document.createElement("liz-search");
    lizSearch.dataset.containerId = container;
    lizSearch.theme = "light";
    lizSearch.variant = "default";
    lizSearch.apiUrl = "http://localhost:8000";
    const i = document.getElementById(container);
    i.parentNode.insertBefore(lizSearch, i);
  };
  document.head.appendChild(s);
})();
