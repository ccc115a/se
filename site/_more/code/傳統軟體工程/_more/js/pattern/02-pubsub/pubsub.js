import EventEmitter from "https://deno.land/x/events/mod.ts";

class MQ {
  constructor () {
    this.emitter = new EventEmitter()
  }
  pub () {
    this.emitter.emit(...arguments)
  }
  sub (event, f) {
    this.emitter.on(event, f)
  }
}

var mq = new MQ()

mq.sub('mbox1', (msg) => { console.log('mbox1:', msg) })

console.log('20181008')
mq.pub('mbox1', 'You have a meeting today')

console.log('20181009')
mq.pub('mbox1', 'Nothing important today')
