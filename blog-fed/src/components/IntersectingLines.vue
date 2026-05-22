<template>
  <canvas ref="canvas" class="intersecting-lines"></canvas>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const canvas = ref(null);
let ctx = null;
let cw = 0;
let ch = 0;
let cx = 0;
let cy = 0;
let linesNum = 10;
let linesRy = [];
let requestId = null;

class Line {
  constructor(flag) {
    this.flag = flag;
    this.a = {};
    this.b = {};
    this.reset();
    this.va = randomIntFromInterval(35, 120) / 100;
    this.vb = randomIntFromInterval(35, 120) / 100;
    this.color = `rgba(${randomIntFromInterval(150, 255)}, ${randomIntFromInterval(150, 255)}, ${randomIntFromInterval(150, 255)}, 0.6)`;
  }

  reset() {
    if (this.flag === "v") {
      this.a.y = 0;
      this.b.y = ch;
      this.a.x = randomIntFromInterval(0, cw);
      this.b.x = randomIntFromInterval(0, cw);
    } else if (this.flag === "h") {
      this.a.x = 0;
      this.b.x = cw;
      this.a.y = randomIntFromInterval(0, ch);
      this.b.y = randomIntFromInterval(0, ch);
    }
  }

  draw() {
    ctx.strokeStyle = this.color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(this.a.x, this.a.y);
    ctx.lineTo(this.b.x, this.b.y);
    ctx.stroke();
  }

  update() {
    if (this.flag === "v") {
      this.a.x += this.va;
      this.b.x += this.vb;
    } else if (this.flag === "h") {
      this.a.y += this.va;
      this.b.y += this.vb;
    }
    this.edges();
  }

  edges() {
    if (this.flag === "v") {
      if (this.a.x < 0 || this.a.x > cw) {
        this.va *= -1;
      }
      if (this.b.x < 0 || this.b.x > cw) {
        this.vb *= -1;
      }
    } else if (this.flag === "h") {
      if (this.a.y < 0 || this.a.y > ch) {
        this.va *= -1;
      }
      if (this.b.y < 0 || this.b.y > ch) {
        this.vb *= -1;
      }
    }
  }
}

function randomIntFromInterval(mn, mx) {
  return ~~(Math.random() * (mx - mn + 1) + mn);
}

function markPoint(p) {
  const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 4);
  gradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)');
  gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
  
  ctx.beginPath();
  ctx.fillStyle = gradient;
  ctx.arc(p.x, p.y, 4, 0, 2 * Math.PI);
  ctx.fill();
}

function Intersect2lines(l1, l2) {
  const p1 = l1.a;
  const p2 = l1.b;
  const p3 = l2.a;
  const p4 = l2.b;
  const denominator = (p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y);
  const ua = ((p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x)) / denominator;
  const ub = ((p2.x - p1.x) * (p1.y - p3.y) - (p2.y - p1.y) * (p1.x - p3.x)) / denominator;
  const x = p1.x + ua * (p2.x - p1.x);
  const y = p1.y + ua * (p2.y - p1.y);
  if (ua > 0 && ub > 0) {
    markPoint({ x, y });
  }
}

function Draw() {
  requestId = window.requestAnimationFrame(Draw);
  ctx.clearRect(0, 0, cw, ch);

  const gradient = ctx.createLinearGradient(0, 0, cw, ch);
  gradient.addColorStop(0, 'rgba(0, 0, 0, 0.1)');
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0.05)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, cw, ch);

  for (let i = 0; i < linesRy.length; i++) {
    const l = linesRy[i];
    l.draw();
    l.update();
  }
  
  for (let i = 0; i < linesRy.length; i++) {
    const l = linesRy[i];
    for (let j = i + 1; j < linesRy.length; j++) {
      const l1 = linesRy[j];
      Intersect2lines(l, l1);
    }
  }
}

function Init() {
  if (requestId) {
    window.cancelAnimationFrame(requestId);
    requestId = null;
  }

  cw = canvas.value.width = window.innerWidth;
  ch = canvas.value.height = window.innerHeight;
  cx = cw / 2;
  cy = ch / 2;

  if (linesRy.length === 0) {
    for (let i = 0; i < linesNum; i++) {
      const flag = i % 2 === 0 ? "h" : "v";
      const l = new Line(flag);
      linesRy.push(l);
    }
  } else {
    linesRy.forEach(line => line.reset());
  }

  Draw();
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

onMounted(() => {
  ctx = canvas.value.getContext("2d");
  Init();
  
  const debouncedResize = debounce(() => {
    Init();
  }, 250);
  
  window.addEventListener('resize', debouncedResize);
});

onBeforeUnmount(() => {
  if (requestId) {
    window.cancelAnimationFrame(requestId);
  }
  window.removeEventListener('resize', debouncedResize);
});
</script>

<style scoped>
.intersecting-lines {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none;
  background: transparent;
}
</style> 