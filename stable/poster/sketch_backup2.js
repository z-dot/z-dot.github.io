var Engine = Matter.Engine,
    World = Matter.World,
    Bodies = Matter.Bodies;



function preload() {
  oxygenFont = loadFont('assets/OxygenMono-Regular.ttf');
  robotoFont = loadFont('assets/RobotoMono-Regular.ttf');
}

function setup() {
  createCanvas(794, 1123);
  engine = Engine.create();
  a_box = Bodies.rectangle(100, 200, 110, 110, {angle: PI * 3 / 16, isStatic: true});
  a_rect = Bodies.rectangle(350, 400, 200, 40, {angle: -0.15, isStatic: true});
  a_circle = Bodies.circle(100, 700, 150, { isStatic: true });
  a_triangle = Bodies.polygon(300, 975, 3, 86, { isStatic: true });
  a_dropping_ball = Bodies.circle(125, 0, 50);
  World.add(engine.world, [a_box, a_rect, a_circle, a_triangle, a_dropping_ball]);
  Engine.run(engine);
}

const w = 794;
const h = 1123;


function serial() {
  push();
  textFont(robotoFont);
  textSize(120);
  fill(255);
  text('Serial', 250, 150);
  text('Killers', 250, 250);
  pop();
}

function early() {
  push();
  textFont(robotoFont);
  textSize(100);
  fill(255);
  text('& Early', 250, 550);
  pop();
}

function childhood() {
  push();
  textFont(robotoFont);
  textSize(100);
  fill(255);
  text('Childhood', 250, 640);
  pop();
}

function trauma() {
  push();
  textFont(robotoFont);
  textSize(100);
  fill(255);
  text('Trauma', 250, 730);
  pop();
}


function draw() {
  background(0);
  push();
  noStroke();
  fill(255);
  push()
  // SQUARE
  translate(a_box.position.x, a_box.position.y);
  rotate(a_box.angle)
  beginShape();
  for (v of a_box.vertices) {
    vertex(v.x - a_box.position.x, v.y - a_box.position.y);
  }
  endShape(CLOSE);
  pop();
  push();
  // RECTANGLE
  translate(a_rect.position.x, a_rect.position.y);
  rotate(a_rect.angle)
  beginShape();
  for (v of a_rect.vertices) {
    vertex(v.x - a_rect.position.x, v.y - a_rect.position.y);
  }
  endShape(CLOSE);
  pop();
  push();
  // CIRCLE
  translate(a_circle.position.x, a_circle.position.y);
  circle(0, 0, a_circle.circleRadius);
  pop();
  push();
  // TRIANGLE
  translate(a_triangle.position.x, a_triangle.position.y);
  rotate(a_triangle.angle)
  beginShape();
  for (v of a_triangle.vertices) {
    vertex(v.x - a_triangle.position.x, v.y - a_triangle.position.y);
  }
  endShape(CLOSE);
  pop();
  push();
  // DROPPING BALL
  translate(a_dropping_ball.position.x, a_dropping_ball.position.y);
  circle(0, 0, a_dropping_ball.circleRadius);
  pop();
  pop();
  serial();
  early();
  childhood();
  trauma();
}
