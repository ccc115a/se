import AutoPilot from 'https://deno.land/x/autopilot@0.2.1/mod.ts';

// create a new AutoPilot instance.
var pilot = new AutoPilot();

// type a string
await pilot.type("Yay! This works");

// alert something
await pilot.alert("This is a alert");

// get screen size
await pilot.screenSize();

// move mouse
await pilot.moveMouse(200, 400);

// take a full-screen screenshot
await pilot.screenshot("screenshot.png");