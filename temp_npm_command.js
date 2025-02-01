import express from "express";
import { spawn } from "child_process";

const app = express();

// Route to trigger command execution
app.get("/run/:param", (req, res) => {
  const param = req.params.param;

  console.log(`Executing command with param: ${param}`);

  // Spawn a child process to run the npm command
  const cmd = spawn("npm", ["run", param]);

  // Capture stdout and send as response
  let output = "";
  cmd.stdout.on("data", (data) => {
    output += data.toString();
  });

  cmd.on("close", (code) => {
    console.log(`Command exited with code ${code}`);
    res.send(output);
  });
});

// Start the server
app.listen(3000, () => {
  console.log("API server listening on port 3000");
});

// Run command every 5 minutes
setInterval(() => {
  console.log("Triggering periodic command execution");

  // Make an HTTP request to the /run route
  fetch("http://localhost:3000/run/myParam")
    .then((res) => res.text())
    .then((output) => {
      console.log("Command output:");
      console.log(output);
    });
}, 5 * 60 * 1000);
