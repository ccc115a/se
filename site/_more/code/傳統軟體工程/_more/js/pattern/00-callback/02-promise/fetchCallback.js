fetch('https://jsonplaceholder.typicode.com/todos/1').then(function (res) {
  res.text().then(function (text) {
    console.log(text)
  })
})

