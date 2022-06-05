function weatherBalloon() {
  fetch('https://api.openweathermap.org/data/2.5/onecall?lat=37.86202&lon=-84.6616&exclude=current,minutely,hourly,alerts&appid=APIKEYHERE')
  .then(function(resp) { return resp.json() })
  .then(function(data) {
    drawWeather(data.daily);
  })
}

function drawWeather(d) {
    for (let day = 0; day < 7; day++) {
      var celcius = Math.round(parseFloat(d[day].temp.day)-273.15);
      var fahrenheit = Math.round(((parseFloat(d[day].temp.day)-273.15)*1.8)+32);
      var dt_txt = new Date(d[day].dt*1000)
      var day_plus = day + 1
      var element = 'day' + day_plus
      document.getElementById(element).innerHTML =
      '<h3>${dt_txt.toLocaleDateString('en-us', {day:"numeric", weekday:"short", month:"short"})}</h3><img src="http://openweathermap.org/img/wn/${d[day].weather[0].icon}@2x.png"><h4> ${fahrenheit}&deg; f</h4>'
    }
}

window.onload = function() {
  weatherBalloon();
}