(function(t){function a(a){for(var s,o,i=a[0],c=a[1],l=a[2],d=0,g=[];d<i.length;d++)o=i[d],Object.prototype.hasOwnProperty.call(r,o)&&r[o]&&g.push(r[o][0]),r[o]=0;for(s in c)Object.prototype.hasOwnProperty.call(c,s)&&(t[s]=c[s]);p&&p(a);while(g.length)g.shift()();return n.push.apply(n,l||[]),e()}function e(){for(var t,a=0;a<n.length;a++){for(var e=n[a],s=!0,o=1;o<e.length;o++){var c=e[o];0!==r[c]&&(s=!1)}s&&(n.splice(a--,1),t=i(i.s=e[0]))}return t}var s={},r={app:0},n=[];function o(t){return i.p+"js/"+({about:"about"}[t]||t)+"."+{about:"2aeb73a3"}[t]+".js"}function i(a){if(s[a])return s[a].exports;var e=s[a]={i:a,l:!1,exports:{}};return t[a].call(e.exports,e,e.exports,i),e.l=!0,e.exports}i.e=function(t){var a=[],e=r[t];if(0!==e)if(e)a.push(e[2]);else{var s=new Promise((function(a,s){e=r[t]=[a,s]}));a.push(e[2]=s);var n,c=document.createElement("script");c.charset="utf-8",c.timeout=120,i.nc&&c.setAttribute("nonce",i.nc),c.src=o(t);var l=new Error;n=function(a){c.onerror=c.onload=null,clearTimeout(d);var e=r[t];if(0!==e){if(e){var s=a&&("load"===a.type?"missing":a.type),n=a&&a.target&&a.target.src;l.message="Loading chunk "+t+" failed.\n("+s+": "+n+")",l.name="ChunkLoadError",l.type=s,l.request=n,e[1](l)}r[t]=void 0}};var d=setTimeout((function(){n({type:"timeout",target:c})}),12e4);c.onerror=c.onload=n,document.head.appendChild(c)}return Promise.all(a)},i.m=t,i.c=s,i.d=function(t,a,e){i.o(t,a)||Object.defineProperty(t,a,{enumerable:!0,get:e})},i.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},i.t=function(t,a){if(1&a&&(t=i(t)),8&a)return t;if(4&a&&"object"===typeof t&&t&&t.__esModule)return t;var e=Object.create(null);if(i.r(e),Object.defineProperty(e,"default",{enumerable:!0,value:t}),2&a&&"string"!=typeof t)for(var s in t)i.d(e,s,function(a){return t[a]}.bind(null,s));return e},i.n=function(t){var a=t&&t.__esModule?function(){return t["default"]}:function(){return t};return i.d(a,"a",a),a},i.o=function(t,a){return Object.prototype.hasOwnProperty.call(t,a)},i.p="/",i.oe=function(t){throw console.error(t),t};var c=window["webpackJsonp"]=window["webpackJsonp"]||[],l=c.push.bind(c);c.push=a,c=c.slice();for(var d=0;d<c.length;d++)a(c[d]);var p=l;n.push([0,"chunk-vendors"]),e()})({0:function(t,a,e){t.exports=e("56d7")},"034f":function(t,a,e){"use strict";var s=e("85ec"),r=e.n(s);r.a},"38f9":function(t,a,e){t.exports=e.p+"img/setup-tecnorepo.c4ff2abd.jpg"},"49f8":function(t,a,e){var s={"./en.json":"edd4","./es.json":"a306","./gal.json":"963c","./pt.json":"5d67"};function r(t){var a=n(t);return e(a)}function n(t){if(!e.o(s,t)){var a=new Error("Cannot find module '"+t+"'");throw a.code="MODULE_NOT_FOUND",a}return s[t]}r.keys=function(){return Object.keys(s)},r.resolve=n,t.exports=r,r.id="49f8"},"55d4":function(t,a){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAXCAYAAACBMvbiAAADdElEQVRIS72WXWxTZRjHf6ed3SjdxrbCNLhaZB2yLZnoMDgFxcwNhxqHyHZjxOAHceECE70hKl4YTVDwI5li0HgBmTEGOgUxy9DUiA4cbGIXBq6xGXGMSl1XerBdz4c5Mw0d7c7pCvPcnTz/5//8nue8531fgd29Klc9y+db6XlsKSbh6sjsvgvpYBIlD60pp8lROLsESe66MJquqiiP/scryfkfxiSs7/KpX/4xZth9xwOLaC0vTquTZQmzOcfQw0ggqKqq+sIxKr8YYEJJWT5T8hflWxjcUI3FfGUxxSWJtp17+fjljUa1DOOTMAnVJo+fT88EDZN2r3RwW+BXfKe/ISqOEBJt2Evs5BcU8XBzGzabzdAjnWAKjCb4U5zA9fkA/8jKtIaCqnC3dIptB/bReOR7DtbfQumwiHV5I75Hamhueen6wCRctv50jne9gWlNG8a/ZptnB8roZWLLHKium3G4T+DsDmK1zr2+MJrbxajE4g4v4bicYm6KR3HL9QR9BdhE8NjLuSMvwNPbf88KREtK+UzpnLb3jvD6yfNXQqoCvcdBVciNhCjPERkUirnJPo+FVjM9b2zKCigjGM05PCFza4eXYEyahGj5q4+e0Sh/xwWerS5kpzfKC0ssdA6N0ffOFubPmfmvnjFMotVdpy7w4s/DFJw8RhgLxeY4b6128Fz3eUrNMS5IJqhdwZaqBbx/T9mMJjRjGM09MiHx5JufcDwQw4TCB00u1nf62eiag3soRPDO+yYh8swmzrZUUWazZASVFYwsy9jb2gmpuUjPPI/ZBK/9cC97hjYwEv9vMsnPU64SPlvtNATKCkZRFBpf+ZC+oExYVvE0vEpd9w5ay+DQsMil2lUphW8wCQw8UYmrME9n/0ragQ3RkwSlm98joGrGAh/dvovN/VtxWmL4cwugonpaq2bnPPY3LE4bz2oymtPhXwZo2nOUZdbf+G5dO0V727GgUFG/Cu9YVLcv7Wg7sW4pNSXWKbqsYTSX8YjI224P/mCEtTVOWu+/a9L823PjPHR4yHDQ9Qvz6VpbQeLYvSYYvWraBaCuc5BjAVEXSgP58dEl1N1oy2wHNmxRR3B0NMLKr86gfzmBFQvmzj6MxqmBPHjwLEdGLulPKfk+cy0TyCS3/+Jlag+cRp5mTLO2ZvTgmrt8uP2hFMm/gBxoxIz6cK8AAAAASUVORK5CYII="},"56d7":function(t,a,e){"use strict";e.r(a);e("e260"),e("e6cf"),e("cca6"),e("a79d");var s=e("2b0e"),r=function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{attrs:{id:"app"}},[e("Header"),e("Banner"),e("Projects"),e("Footer")],1)},n=[],o=function(){var t=this,a=t.$createElement,s=t._self._c||a;return s("header",{staticClass:"header_area white_menu",attrs:{id:"index"}},[s("div",{staticClass:"main_menu",attrs:{id:"mainNav"}},[s("nav",{staticClass:"navbar navbar-expand-lg navbar-light"},[s("div",{staticClass:"container"},[t._m(0),t._m(1),s("div",{staticClass:"collapse navbar-collapse offset",attrs:{id:"navbarSupportedContent"}},[s("ul",{staticClass:"nav navbar-nav menu_nav ml-auto"},[s("li",{staticClass:"nav-item dropdown"},[s("a",{staticClass:"nav-link",attrs:{id:"dropdown09","data-toggle":"dropdown","aria-haspopup":"true","aria-expanded":"false"}},[s("button",{staticClass:"ico_bandera  flag_button nav-link btn btn-transparent"},[s("img",{staticClass:"flag_languages w-8 h-8",attrs:{src:e("bad3")("./flag_"+t.$i18n.locale+".png"),alt:"flag"}}),s("span",{staticClass:"ml-2"},[t._v(t._s(t.$i18n.locale.toUpperCase()))]),s("svg",{attrs:{fill:"currentColor",xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 24 24",width:"24",height:"24"}},[s("path",{staticClass:"heroicon-ui",attrs:{d:"M15.3 9.3a1 1 0 0 1 1.4 1.4l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 0 1 1.4-1.4l3.3 3.29 3.3-3.3z"}})])])]),s("div",{staticClass:"flag_windows dropdown-menu",attrs:{"aria-labelledby":"dropdown09"}},[s("a",{staticClass:"dropdown-item",attrs:{href:"#en"},on:{click:function(a){return a.preventDefault(),t.setLocale("gal")}}},[s("img",{staticClass:" h-8 w-8",attrs:{src:e("55d4"),alt:"galician flag"}}),s("span",{staticClass:"ml-2"},[t._v("GAL")])]),s("a",{staticClass:"dropdown-item",attrs:{href:"#en"},on:{click:function(a){return a.preventDefault(),t.setLocale("es")}}},[s("img",{staticClass:" h-8 w-8",attrs:{src:e("8ede"),alt:"espanish flag"}}),s("span",{staticClass:"ml-2"},[t._v("ES")])]),s("a",{staticClass:"dropdown-item",attrs:{href:"#en"},on:{click:function(a){return a.preventDefault(),t.setLocale("en")}}},[s("img",{staticClass:" h-8 w-8",attrs:{src:e("d15e"),alt:"english flag"}}),s("span",{staticClass:"ml-2"},[t._v("EN")])]),s("a",{staticClass:"dropdown-item",attrs:{href:"#en"},on:{click:function(a){return a.preventDefault(),t.setLocale("pt")}}},[s("img",{staticClass:" h-8 w-8",attrs:{src:e("8d80"),alt:"portuguese flag"}}),s("span",{staticClass:"ml-2"},[t._v("PT")])])])])])])])])])])},i=[function(){var t=this,a=t.$createElement,s=t._self._c||a;return s("a",{staticClass:"navbar-brand logo_h"},[s("img",{attrs:{src:e("cf05"),alt:""}})])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("button",{staticClass:"navbar-toggler",attrs:{type:"button","data-toggle":"collapse","data-target":"#navbarSupportedContent","aria-controls":"navbarSupportedContent","aria-expanded":"false","aria-label":"Toggle navigation"}},[e("span",{staticClass:"icon-bar"}),e("span",{staticClass:"icon-bar"}),e("span",{staticClass:"icon-bar"})])}],c={methods:{setLocale:function(t){this.$i18n.locale=t,this.$router.push({params:{lang:t}}),this.hideDropdown()}}},l=c,d=e("2877"),p=Object(d["a"])(l,o,i,!1,null,null,null),g=p.exports,b=function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("section",{staticClass:"home_banner_area"},[e("div",{staticClass:"banner_inner"},[e("div",{staticClass:"container"},[e("div",{staticClass:"row"},[e("div",{staticClass:"col-lg-3"}),e("div",{staticClass:"col-lg-6"},[e("div",{staticClass:"banner_content home_left_img"},[e("h5",[t._v(t._s(t.$t("banner.hi")))]),e("h2",[t._v(t._s(t.$t("banner.name")))]),e("h5",[t._v(t._s(t.$t("banner.job")))]),t._m(0)])]),e("div",{staticClass:"col-lg-3"})])])])])},u=[function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("h4",[e("a",{staticClass:"social-web-banner-m",attrs:{href:"https://www.github.com/toniferr",target:"_blank"}},[e("i",{staticClass:"fab fa-github social-web-banner"})]),e("a",{staticClass:"social-web-banner-m",attrs:{href:"https://es.linkedin.com/in/antonio-ferreiro-couto",target:"_blank"}},[e("i",{staticClass:"fab fa-linkedin social-web-banner"})]),e("a",{staticClass:"email social-web-banner-m",attrs:{href:"mailto:ferreirocouto@gmail.com",target:"_blank"}},[e("i",{staticClass:"fas fa-envelope social-web-banner"})])])}],f={},v=Object(d["a"])(f,b,u,!1,null,null,null),m=v.exports,h=function(){var t=this,a=t.$createElement,s=t._self._c||a;return s("section",{staticClass:"projects_area p_120",attrs:{id:"proyectos"}},[s("div",{staticClass:"container"},[s("div",{staticClass:"main_title"},[s("h2",[t._v(t._s(t.$t("github.projects")))]),s("p",[t._v(t._s(t.$t("github.definition1"))+" "),s("a",{attrs:{href:"https://github.com/toniferr",target:"_blank"}},[t._v("Github")]),t._v(" "+t._s(t.$t("github.definition2")))])]),s("div",{staticClass:"projects_inner row"},[s("div",{staticClass:"col-lg-4 col-sm-6 spring"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("8c0e"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.eurosnovos")))])]),t._m(0)])]),s("div",{staticClass:"col-lg-4 col-sm-6 swing"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("9b4e"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.cryptokit")))])]),t._m(1)])]),s("div",{staticClass:"col-lg-4 col-sm-6 spring"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("afba"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.representados")))])]),t._m(2)])]),s("div",{staticClass:"col-lg-4 col-sm-6 javascript"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("a804"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.io")))])]),t._m(3)])]),s("div",{staticClass:"col-lg-4 col-sm-6 struts"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("38f9"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.angular")))])]),t._m(4)])]),s("div",{staticClass:"col-lg-4 col-sm-6 javascript"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("56f6"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.express")))])]),t._m(5)])]),s("div",{staticClass:"col-lg-4 col-sm-6"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("84e8"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.peeperpattern")))])]),s("div",{staticClass:"overlay"},[t._m(6),s("div",{staticClass:"badges-projects"},[s("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v(t._s(t.$t("github.pattern")))]),s("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("uml")]),s("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("java")])])])])]),s("div",{staticClass:"col-lg-4 col-sm-6"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("7c49"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.peepermaven")))])]),t._m(7)])]),s("div",{staticClass:"col-lg-4 col-sm-6"},[s("div",{staticClass:"projects_item"},[s("img",{staticClass:"img-fluid",attrs:{src:e("f306"),alt:""}}),s("div",{staticClass:"projects_text"},[s("h4",[t._v(t._s(t.$t("github.peeperandroid")))])]),t._m(8)])])])])])},C=[function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/eurosnovos",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-left",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("a",{attrs:{href:"https://euros-novos.herokuapp.com/",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-open-right",attrs:{type:"button"}},[e("i",{staticClass:"fa fa-link",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-boot")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-security")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("thymeleaf")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("maven")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-data")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("jpa")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("mysql")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/cryptokit",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-left",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("a",{attrs:{href:"https://github.com/toniferr/cryptoKit/raw/master/download",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-open-right",attrs:{type:"button"}},[e("i",{staticClass:"fa fa-download",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("java-swing")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("maven")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("jca")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("bouncycastle")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://representa2.herokuapp.com/",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fa fa-link",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-boot")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-security")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("thymeleaf")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("maven")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("cloudinary")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("spring-data")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("jpa")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("postgree")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/dev.toniferr.github.io",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-left",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("a",{attrs:{href:"https://toniferr.github.io",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-open-right",attrs:{type:"button"}},[e("i",{staticClass:"fa fa-link",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("vuejs")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("javascript")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("html")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("css")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("portfolio")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/portfolio-angular",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("angular")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("typescript")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("javascript")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("html")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("css")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/peepernode",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("nodejs")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("express")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("mongoose")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("mongodb")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("javascript")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("a",{attrs:{href:"https://github.com/toniferr/PeeperPattern",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/PeeperMaven",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("maven")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("plugins")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("java")])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"overlay"},[e("a",{attrs:{href:"https://github.com/toniferr/PeeperAndroid",target:"_blank"}},[e("button",{staticClass:"btn btn-dark button-git-center",attrs:{type:"button"}},[e("i",{staticClass:"fab fa-github",attrs:{"aria-hidden":"true"}})])]),e("div",{staticClass:"badges-projects"},[e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("java")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("android-studio")]),e("span",{staticClass:"badge bg-warning text-dark badge-project"},[t._v("gradle")])])])}],j={},w=Object(d["a"])(j,h,C,!1,null,null,null),_=w.exports,x=function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("footer",{staticClass:"footer_area",attrs:{id:"footer"}},[e("div",{staticClass:"container"},[e("div",{staticClass:"row footer_inner"},[t._m(0),e("div",{staticClass:"col-lg-6 col-sm-12 footer-m"},[e("aside",{staticClass:"f_widget ab_widget"},[e("div",{staticClass:"f_title"},[e("h3",[t._v(t._s(t.$t("footer.about")))])]),e("p",[t._v(t._s(t.$t("footer.aboutprofesional")))])])]),e("div",{staticClass:"col-lg-3 col-sm-12 footer-m"},[e("aside",{staticClass:"f_widget social_widget"},[e("div",{staticClass:"f_title"},[e("h3",[t._v(t._s(t.$t("footer.contact")))])]),t._m(1)])])]),e("div",{staticClass:"row footer_inner footer-copy"},[t._m(2),e("div",{staticClass:"col-lg-4 col-sm-12 footer-m"},[e("aside",{staticClass:"f_widget social_widget"},[e("p",[t._v(t._s(t.$t("footer.aboutweb"))+" "),e("a",{attrs:{href:"https://es.vuejs.org/"}},[t._v("Vue.js")])])])]),t._m(3)])])])},A=[function(){var t=this,a=t.$createElement,s=t._self._c||a;return s("div",{staticClass:"col-lg-3 col-sm-12 footer-m"},[s("aside",{staticClass:"f_widget social_widget"},[s("img",{staticClass:"foto-footer",attrs:{src:e("7bd1"),alt:""}})])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("ul",{staticClass:"list"},[e("li",[e("a",{attrs:{href:"https://www.github.com/toniferr",target:"_blank"}},[e("i",{staticClass:"fab fa-github"})])]),e("li",[e("a",{attrs:{href:"https://es.linkedin.com/in/antonio-ferreiro-couto",target:"_blank"}},[e("i",{staticClass:"fab fa-linkedin"})])]),e("li",[e("a",{attrs:{href:"mailto:ferreirocouto@gmail.com",target:"_blank"}},[e("i",{staticClass:"far fa-envelope"})])])])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"col-lg-4 col-sm-12 footer-m"},[e("aside",{staticClass:"f_widget social_widget"})])},function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"col-lg-4 col-sm-12 footer-m"},[e("aside",{staticClass:"f_widget social_widget"})])}],k={},y=Object(d["a"])(k,x,A,!1,null,null,null),E=y.exports,O={name:"App",components:{Header:g,Banner:m,Projects:_,Footer:E}},S=O,P=(e("034f"),Object(d["a"])(S,r,n,!1,null,null,null)),U=P.exports,M=(e("4160"),e("d3b7"),e("ac1f"),e("466d"),e("159b"),e("ddb0"),e("a925"));function R(){var t=e("49f8"),a={};return t.keys().forEach((function(e){var s=e.match(/([A-Za-z0-9-_]+)\./i);if(s&&s.length>1){var r=s[1];a[r]=t(e)}})),a}s["a"].use(M["a"]);var W=new M["a"]({locale:"gal",fallbackLocale:"es",messages:R()}),I=e("8c4f"),N=function(){var t=this,a=t.$createElement,s=t._self._c||a;return s("div",{staticClass:"home"},[s("img",{attrs:{alt:"Vue logo",src:e("cf05")}}),s("HelloWorld",{attrs:{msg:"Welcome to Your Vue.js App"}})],1)},B=[],T=function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticClass:"hello"},[e("h1",[t._v(t._s(t.msg))])])},L=[],G={name:"HelloWorld",props:{msg:String}},V=G,H=Object(d["a"])(V,T,L,!1,null,null,null),F=H.exports,Y={name:"Home",components:{HelloWorld:F}},J=Y,Q=Object(d["a"])(J,N,B,!1,null,null,null),Z=Q.exports;s["a"].use(I["a"]);var z=[{path:"/",redirect:"/".concat(W.locale)},{path:"/:lang",redirect:"/".concat(W.locale)},{path:"/:lang",component:{render:function(t){return t("router-view")}},children:[{path:"/",name:"Home",component:Z},{path:"/about",name:"About",component:function(){return e.e("about").then(e.bind(null,"f820"))}}]}],K=new I["a"]({mode:"history",base:"/",routes:z}),q=K;e("4989"),e("c5ec"),e("e609"),e("f9e3"),e("15f5"),e("7051");s["a"].config.productionTip=!1,q.beforeEach((function(t,a,e){var s=t.params.lang;s||(s="gal"),W.locale=s,e()})),new s["a"]({i18n:W,router:q,render:function(t){return t(U)}}).$mount("#app")},"56f6":function(t,a,e){t.exports=e.p+"img/express.86e82358.jpg"},"5d67":function(t){t.exports=JSON.parse('{"nav":{"projects":"Projetos","about":"Sobre mim"},"banner":{"hi":"Olá! Eu sou","name":"Antonio Ferreiro","job":"Engenheiro de software"},"github":{"projects":"Projetos & Trabalhos","definition1":"Estes são alguns dos meus projetos pessoais ","definition2":". Aqui guardo o código de trabalhos dos meus cursos (os chamo Peeper*), bem como o código dos projetos feitos por mim.","eurosnovos":"Euros Novos","cryptokit":"CryptoKit","representados":"Representados","angular":"Portfolio-angular","express":"PeeperNode","peeperpattern":"PeeperPattern","pattern":"padrões de desenho","peepermaven":"PeeperMaven","io":"Github.io","peeperandroid":"PeeperAndroid"},"footer":{"about":"Sobre mim","aboutprofesional":"Sou galego e moro na Galiza (Espanha). Estudei Engenharia da Computação na Universidade de Vigo e desde 2016 trabalho como engenheiro de software.","aboutweb":"© 2020, Feito com ","contact":"Contato"}}')},"7bd1":function(t,a,e){t.exports=e.p+"img/toni.89af8339.jpg"},"7c49":function(t,a,e){t.exports=e.p+"img/peepermaven.0a51640f.jpg"},"84e8":function(t,a,e){t.exports=e.p+"img/peeperpattern.5b9088d6.jpg"},"85ec":function(t,a,e){},"8c0e":function(t,a,e){t.exports=e.p+"img/eurosnovos.c8f2720e.jpg"},"8d80":function(t,a){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAXCAYAAACBMvbiAAACcklEQVRIS+2WTUiTcRzHP3t/5rbcnI8vaGaFiYItKkMxskslWQerQxReylOXyA5lXTpFIUFQ1xA0L70QVEJBZI6EIKkURbJV25yxMnTv7fV5YlGXwKYz67L/+feDz//z+/5fFBzbIpPFcti/ZtH15xZFDmYBQTkzCyVnyWYMqhRV+RF6xwJoZzSoY8q/FuRFwxTp4jw47OD+uJFJr45OZwT92iQFTTHCXSJCQLVsqEXB5GsSdDdMc8leTiShpVGco9MZRpwwEDImkdt9GHvy0USWB5QRZpU6yciJKaIjembCYaqulTB9aA6UMqtvWXl70otxVCTVMEvBVRFjNHugjDDnN7s5WOPDZLei6NexZmIKpzeEJMtUinqmbbUEtiqI+cMYbHHy7pizHldGmN4WB4JSos4t4H6eorlvhuFxL5Is0VRbhL2jgtIiExp9EGlDDOGyuDIwaoXMBdsHrk+UsTsh0179EUfFIENvPMQTEs22Emq8e7A+LkMZiBDY76f0phWlrMgKKKOZ/lYHg04Te916Ng7EsTx6yssvMpIkU18o49+3i/gRFQTnUdTF0FxcITPp7XXVe3gyZeLUJg3KgU+IOxupbO37AeMaaGd+6AX1p4uJ+1xEhwTybq9gZiyqOHfb3nHuWTlnKEaccSG+EkCG2W0xkmvWsb5tGEFW4jouYg6psxpRuinjmNJFBboE3dtdXHldxlzQQIsuSocngsUFGvM3Qgd86G5Y0AWyB1k0TLqwRBfj4dH33Bs1Mvn55w1cmaRwR4zg2UIE3/JAlgTzy71RnaLaHKFnzI/Wo0Ud/Q9v0+9ByP30FjoaOTP/0sx3t+kS2fROC5YAAAAASUVORK5CYII="},"8ede":function(t,a){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAAXCAYAAACBMvbiAAABu0lEQVRIS+2WTU9TQRSGn5mbSr2mlVDbqgS7kBRsRVKFCiYkLNyhLNEdCSGsXDThtxB+gQs3rohsTDRBBdNWSAVioBAgxEbCRyzWttzeO6Yx0VURkutNF53tSeY8M+ec97ziw6Ubijo5ogFToxKNn6nVomJ10K+UIZBuhflToukWVkkgXL/72smYUHP8nSZRzV6roP8/JtS7mun/UCklsBQs51xErxoIAZq0XxHOBJNacXHw0svXWxdpSZUJD/0gdN9Av1CxVaH+CVN9/+q6ZOH5FUy9gHai4wnnGRkp2wpSvexUmIolWN7QkOkm0isaKu/j8vAjOrtMOnzTrO1KIiHTNqhTYU5EkCOzm+Rkmo/3SkTnb+J/mqApfJ3ewCjfVYSAfOMMzMZ7nWymlf3MIdshg9xRjN4Hg4R6InhS4xRKfgaebDoDszQbwHe3lcUvnykuuvm01k68bQtPi2BgTPJ6qovHibfOwBjKy54RJZNMcpx2Uwl48B6WkGXFw4TFt2IHbXrSGZjsQZCZbJyJOzOs52LM7vXR3Zynv/kF21xjbuc2z+KvbISpJwWuq93UMFcNc3XOOasr2/kLDvMPGxoRI/oAAAAASUVORK5CYII="},"963c":function(t){t.exports=JSON.parse('{"nav":{"projects":"Proxectos","about":"Sobre min"},"banner":{"hi":"Ola! Eu son","name":"Antonio Ferreiro","job":"Enxeñeiro de software"},"github":{"projects":"Proxectos & Traballos","definition1":"Estes son algúns dos meus proxectos e traballos persoais do meu ","definition2":". Aquí gardo o código dos traballos dos meus cursos (chámolles Peeper*) así como tamén o código de proxectos realizados pola miña conta.","eurosnovos":"Euros Novos","cryptokit":"CryptoKit","representados":"Representados","angular":"Portfolio-angular","express":"PeeperNode","peeperpattern":"PeeperPattern","pattern":"patróns de deseño","peepermaven":"PeeperMaven","io":"Github.io","peeperandroid":"PeeperAndroid"},"footer":{"about":"Sobre min","aboutprofesional":"Son galego e vivo en Galiza (España). Estudei enxeñaría informática na Universidade de Vigo e dende 2016 estou traballando como enxeñeiro de software.","aboutweb":"© 2020, Feito con ","contact":"Contacto"}}')},"9b4e":function(t,a,e){t.exports=e.p+"img/cryptokit.f3c3cbbc.jpg"},a306:function(t){t.exports=JSON.parse('{"nav":{"projects":"Proyectos","about":"Sobre mí"},"banner":{"hi":"Hola! Soy","name":"Antonio Ferreiro","job":"Ingeniero de software"},"github":{"projects":"Proyectos & Trabajos","definition1":"Estos son algunos de mis proyectos personales ","definition2":". Aquí guardo el código de trabajos de mis cursos (los llamo Peeper*) así como también el código de proyectos realizados por mi cuenta.","eurosnovos":"Euros Novos","cryptokit":"CryptoKit","representados":"Representados","angular":"Portfolio-angular","express":"PeeperNode","peeperpattern":"PeeperPattern","pattern":"patrones de diseño","peepermaven":"PeeperMaven","io":"Github.io","peeperandroid":"PeeperAndroid"},"footer":{"about":"Sobre mí","aboutprofesional":"Soy gallego y vivo en Galicia (España). Estudié ingeniería informática en la Universidad de Vigo y desde 2016 trabajo como ingeniero de software.","aboutweb":"© 2020, Hecho con ","contact":"Contacto"}}')},a804:function(t,a,e){t.exports=e.p+"img/toniferrgithub.7586bee6.jpg"},afba:function(t,a,e){t.exports=e.p+"img/representado.faf2ff2f.jpg"},bad3:function(t,a,e){var s={"./flag_en.png":"d15e","./flag_es.png":"8ede","./flag_gal.png":"55d4","./flag_pt.png":"8d80"};function r(t){var a=n(t);return e(a)}function n(t){if(!e.o(s,t)){var a=new Error("Cannot find module '"+t+"'");throw a.code="MODULE_NOT_FOUND",a}return s[t]}r.keys=function(){return Object.keys(s)},r.resolve=n,t.exports=r,r.id="bad3"},cf05:function(t,a){t.exports="data:image/png;base64,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"},d15e:function(t,a){t.exports="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACMAAAASCAYAAADR/2dRAAAEcklEQVRIS82Wf0yUdRzHX89zxyEH4uGdSCWScopJ6nTkdI1NtALUBpjL3xtZmYjmj0xpLhQ2J5qJpIhZGZu/nYksFagUN9ZkjMm0MJFTw7NC4OQE7tDj7nna86CHTMVaufn95/vs+X4+7/fn+/n5FS5NnC6bj3yNGBiAoNGQf7SKDzNP0Opw0dMaHBpE5UIzdamfeMXCcjcQtdPCVWtzj7q99Tqyl0aTpLdjXZ6O2DsAxQahMf+wXL9xOwHjxmBIiMOQEIurw8OR4mpOlNaw//tfHglsMui5tHQI1uVrveeh2RkMy6mlye58pM7sN0cQPzaUcWcKcZVXoo8aqXIGvhaN6NcLwfTKBrni0LuQnsnt4lJ0YQMYenIv2mCTCni8tIbEhfvxSHI3gohBJs4uCKcuZXWXZ/I2Mn7XFWquNXWT1YgCx3JnMur4AWz7jqrYCofCpay6P+xEJe1EwPypLAoC78+MYn6oB9OpEpwXLvLcqlR6vWTGf+xoEARWZhVTUmah+nIDiln9jQFULzFjXZbe5ZmtmURus3DT1oYARA4NZtJwI+sm9OPmph1qOBTMAevTEHQ6Ll1tYmv+Wb46WIkky53G3Efz0YoMGdiXTYtfJbJgL7eLSvE1DyL8UB4+z4dgb7nDtRvNxMzZjSHQj3Mp4VxfssZrzMBt6xmTdwV7Szun8+ehy9uFdLIYTZBBxVCwBK1WvdSK9UXU1tnocEtefcF3eIbsdnvw9dXibO9A7+eDy+UhY+lEPkqIwBI7C09LK8GL3yFkZYrqJWUdLvqV19t+p25RWleYdmTxY8CLJI7qR+0bM/G0OQhOTSbk40WqjCTJZH1Zxtqc0+h0Gi/f3btutFoNQn1jq+oZWe7kub8r/wRBoF+QH+6mW+q3qPdD9Nd7yW17vsO64oEE3pKBcXYSHTZFnnvy/l75BpsDWSF4HF9V8AgZSVLdJ7vd3h1R7AR5wtlDZfMP9R7FJ1SZIruXSY8d4ukePmPGPEthelICBxu7ElByOJCc7WqS+xj7Yttf8HACz3vLG0vJ4bwnL6M19aWxWdHtIYF7Ku20D6IRxc5Srv9sBw25+WgC/Bnyw0GOnW98bGm/Hf9yp0GyTP3mPBq2f4smsDfmkgN8Xljz+NJ+qOmFGdmyJp7YaLNaXXct17gyIwVPsx1xchyulAVMTN7zxKZXum8+gwYEYQjsRcef9SqGgtUnPobqpLms2v4ztddvdW96D46DZcnjGTbYhOxycWNNFnd+syC1ttF/1SLWnWnk1EXbvx4HyqU2p8WpXnJUVKmYf23KRT9yOE2TYtlt1XSNA2VQVhYsJOwFg+pZV90NLk+ei7uhCeOcaZyfOovE1IP/fVDunM3UmAiVQ8FWOBSuPnExkJnO2BnfIMiyLEvtd2j5qQx7YTHOygvoxkVRPiGBogrr//6EmBITwfS4SHQ+GuyFJSpnW/k5QlYvRnCevyhbpr+nhiM0O5MCp4HlOWW0Op/i48pfxxfpU0ieNhrZ40FqaUOx4W9b2XSwz30k0wAAAABJRU5ErkJggg=="},edd4:function(t){t.exports=JSON.parse('{"nav":{"projects":"Projects","about":"About me"},"banner":{"hi":"Hi there! I\'m","name":"Antonio Ferreiro","job":"Software engineer"},"github":{"projects":"Projects & Works","definition1":"These are some of my personal projects of mine ","definition2":". Here I keep the code of works from my courses (I call them Peeper*) as well as the code of projects made by myself.","eurosnovos":"Euros Novos","cryptokit":"CryptoKit","representados":"Representados","angular":"Portfolio-angular","express":"PeeperNode","peeperpattern":"PeeperPattern","pattern":"design patterns","peepermaven":"PeeperMaven","io":"Github.io","peeperandroid":"PeeperAndroid"},"footer":{"about":"About me","aboutprofesional":"I\'m Galician and I live in Galicia (Spain). I studied computer engineering at the University of Vigo and since 2016 I am working as a software engineering.","aboutweb":"© 2020, Built with ","contact":"Contact"}}')},f306:function(t,a,e){t.exports=e.p+"img/peeperandroid.fdf7dc70.png"}});
//# sourceMappingURL=app.f6dccead.js.map