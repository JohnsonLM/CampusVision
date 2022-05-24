const textList = {{ messages|safe }};
let i = 0;

const cycleText = () => {
  document.getElementById("message-cycle").innerHTML = textList[i];
  i = ++i % textList.length;
};

cycleText();
setInterval(cycleText, {{ interval }});