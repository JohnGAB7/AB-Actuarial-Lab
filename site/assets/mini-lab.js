/* Accessible homepage compound-interest mini-lab. */
(function () {
  "use strict";
  var root = document.getElementById("mini-lab");
  if (!root) return;
  var en = document.documentElement.lang === "en";
  var $ = function (id) { return document.getElementById(id); };
  var capital = $("mini-capital"), rate = $("mini-rate"), years = $("mini-years");
  var capLabel = $("mini-capital-label"), rateLabel = $("mini-rate-label"), yearLabel = $("mini-years-label");
  var future = $("mini-future"), interest = $("mini-interest"), factor = $("mini-factor");
  var canvas = $("mini-growth"), summary = $("mini-chart-summary");
  if (!capital || !rate || !years || !canvas) return;
  var ctx = canvas.getContext("2d");
  var nf = new Intl.NumberFormat(en ? "en-GB" : "fr-FR", {maximumFractionDigits:2});
  var money = function (x) { return nf.format(x); };
  var pct = function (x) { return nf.format(x) + " %"; };
  var yearsText = function (x) { return en ? (x === 1 ? "1 year" : x + " years") : (x === 1 ? "1 an" : x + " ans"); };
  function draw(c, i, n) {
    if (!ctx) return;
    var dpr = Math.max(1, window.devicePixelRatio || 1);
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(280, rect.width), h = 250;
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    var pad = {l:42,r:14,t:16,b:30}, pw=w-pad.l-pad.r, ph=h-pad.t-pad.b;
    var vals = Array.from({length:n+1},function(_,k){return c*Math.pow(1+i,k);});
    var max = Math.max(vals[n],c)*1.08;
    var x = function(k){return pad.l+pw*k/n;}, y=function(v){return pad.t+ph*(1-v/max);};
    ctx.clearRect(0,0,w,h);
    ctx.font="11px system-ui";ctx.fillStyle=getComputedStyle(root).getPropertyValue("--muted");ctx.strokeStyle=getComputedStyle(root).getPropertyValue("--line");
    for(var g=0;g<=3;g++){var v=max*g/3, yy=y(v);ctx.beginPath();ctx.moveTo(pad.l,yy);ctx.lineTo(w-pad.r,yy);ctx.stroke();ctx.fillText(money(v),3,yy+4);}
    ctx.beginPath();ctx.moveTo(x(0),y(vals[0]));for(var k=1;k<=n;k++)ctx.lineTo(x(k),y(vals[k]));
    ctx.strokeStyle=getComputedStyle(root).getPropertyValue("--data");ctx.lineWidth=3;ctx.lineJoin="round";ctx.stroke();
    ctx.lineTo(x(n),pad.t+ph);ctx.lineTo(x(0),pad.t+ph);ctx.closePath();
    ctx.fillStyle=getComputedStyle(root).getPropertyValue("--data-soft");ctx.globalAlpha=.75;ctx.fill();ctx.globalAlpha=1;
    ctx.fillStyle=getComputedStyle(root).getPropertyValue("--muted");ctx.textAlign="center";
    ctx.fillText("0",x(0),h-8);ctx.fillText(String(n),x(n),h-8);
    ctx.fillText(en?"Year":"Année",pad.l+pw/2,h-8);
    ctx.beginPath();ctx.arc(x(n),y(vals[n]),4.5,0,Math.PI*2);ctx.fillStyle=getComputedStyle(root).getPropertyValue("--data");ctx.fill();
    ctx.textAlign="left";
    summary.textContent=(en?"After ":"Après ")+yearsText(n)+", "+(en?"the capital reaches ":"le capital atteint ")+money(vals[n])+".";
  }
  function update() {
    var c=Number(capital.value), i=Number(rate.value)/100, n=Number(years.value);
    var a=c*Math.pow(1+i,n);
    capLabel.textContent=money(c);rateLabel.textContent=pct(Number(rate.value));yearLabel.textContent=yearsText(n);
    future.textContent=money(a);interest.textContent=money(a-c);factor.textContent=money(a/c)+"×";
    draw(c,i,n);
  }
  [capital,rate,years].forEach(function(el){el.addEventListener("input",update);});
  if(window.ResizeObserver){new ResizeObserver(update).observe(canvas.parentElement);}
  else window.addEventListener("resize",update);
  update();
})();
