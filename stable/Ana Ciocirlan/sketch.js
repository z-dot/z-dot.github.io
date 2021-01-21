var Engine = Matter.Engine,
    World = Matter.World,
    Bodies = Matter.Bodies;



function preload() {
  oxygenFont = loadFont('assets/OxygenMono-Regular.ttf');
  robotoFont = loadFont('assets/RobotoMono-Regular.ttf');
}

function setup() {
  createCanvas(794, 1123);
  a_red = color('#FE0000');
  a_yellow = color('#FDEB01');
  a_green = color('#09A603');
  a_blue = color('#035BDF');
  engine = Engine.create();
  hasHappened = {
      square: false,
      rectangle: false,
      circle: false,
      triangle: false
  };
  theCount = 0;
  a_box = Bodies.rectangle(100, 200, 110, 110, {angle: PI * 3 / 16, isStatic: true});
  a_rect = Bodies.rectangle(350, 375, 200, 40, {angle: -0.45, isStatic: true});
  a_circle = Bodies.circle(106, 680, 65, { isStatic: true });
  a_triangle = Bodies.polygon(375, 900, 3, 86, { isStatic: true });
  a_dropping_ball = Bodies.circle(125, 0, 25, {restitution: 0.7});
  World.add(engine.world, [a_box, a_rect, a_circle, a_triangle, a_dropping_ball]);
Matter.Events.on(engine, 'collisionStart', function(event) {
    console.log(event);
    theCount++;
    if (theCount == 1) {
        hasHappened.square = true;
    } else if (theCount == 2) {
        hasHappened.rectangle = true;
    } else if (theCount == 3) {
        hasHappened.circle = true;
    } else if (theCount == 4) {
        hasHappened.triangle = true;
    }
});
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
  if (hasHappened.square) {
    fill(a_red);
  } else {fill(255);}
  beginShape();
  for (v of a_box.vertices) {
    vertex(v.x, v.y);
  }
  endShape(CLOSE);
  pop();
  push();
  // RECTANGLE
  if (hasHappened.rectangle) {
    fill(a_yellow);
  } else {fill(255);}
  beginShape();
  for (v of a_rect.vertices) {
    vertex(v.x, v.y);
  }
  endShape(CLOSE);
  pop();
  push();
  // CIRCLE
  if (hasHappened.circle) {
    fill(a_green);
  } else {fill(255);}
  translate(a_circle.position.x, a_circle.position.y);
  circle(0, 0, a_circle.circleRadius * 2);
  pop();
  push();
  // TRIANGLE
  if (hasHappened.triangle) {
    fill(a_blue);
  } else {fill(255);}
  beginShape();
  for (v of a_triangle.vertices) {
    vertex(v.x, v.y);
  }
  endShape(CLOSE);
  pop();
  pop();
  if (hasHappened.square) {serial();}
  if (hasHappened.rectangle) {early();}
  if (hasHappened.circle) {childhood();}
  if (hasHappened.triangle) {trauma();}
  push();
  // DROPPING BALL
  fill('#F07B00');
  translate(a_dropping_ball.position.x, a_dropping_ball.position.y);
  circle(0, 0, a_dropping_ball.circleRadius * 2);
  pop();
}
