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
  box = Bodies.rectangle(100, 200, 100, 100, {angle: PI * 3 / 16});
  r_rect = Bodies.rectangle(300, 400, 200, 40, {angle: PI * 14/16});
  circ = Bodies.circle(100, 650, 150);
  tri_a = Bodies.polygon(300, 800, 3, 86);
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
  rectMode(RADIUS);
  push()
  translate(100, 200);
  rotate(PI * 3 / 16)
  rect(0, 0, 50);
  pop();
  push();
  translate(300, 400);
  rotate(PI * 14 / 16);
  rect(0, 0, 100, 20);
  pop();
  push();
  translate(100, 650);
  circle(0, 0, 150);
  pop();
  push();
  translate(300, 800);
  rotate(PI * 1/16)
  triangle(0, 0, 100, 173, -100, 173);
  pop();
  pop();
  serial();
  early();
  childhood();
  trauma();
}
