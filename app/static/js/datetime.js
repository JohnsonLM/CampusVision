function clock() {
    var dt = new Date();
    document.getElementById("time").innerHTML = dt.toLocaleTimeString();
    document.getElementById("date").innerHTML = dt.toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
}

setInterval(function() {
    clock();
}, 1000);

setTimeout(function() {
    window.location.reload(true);
}, 1800000);
