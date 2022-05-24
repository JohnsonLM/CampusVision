function clock() {
    var dt = new Date();
    document.getElementById("time").innerHTML = dt.toLocaleTimeString();
    document.getElementById("date").innerHTML = dt.toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
}

setInterval(clock, 1000);
setTimeout("window.location.reload(true)",60 * 1000 * 1)
