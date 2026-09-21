const $ = function (filter) {
  let q = new Q()
  return q.get(filter)
}

class Q {
  constructor () {
    this.filter = ''
    this.nodes = window.document
  }
  get (filter) {
    this.filter += ' ' + filter
    this.nodes = document.querySelectorAll(this.filter)
    return this
  }
  each (f) {
    for (let node of this.nodes) {
      f(node)
    }
    return this
  }
}
