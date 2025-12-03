# Running Examples

This guide shows you how to run the JavaScript API examples.

## Setup

### 1. Install Dependencies

First, navigate to the javascript directory and install the required packages:

```bash
cd javascript
npm install
```

### 2. Build the TypeScript Code

Compile the TypeScript source to JavaScript:

```bash
npm run build
```

This will create a `dist/` directory with the compiled JavaScript files.

### 3. Set Up Environment Variables

Create a `.env` file in the `javascript/` directory with your Hopsworks credentials:

```bash
# Create .env file
cat > .env << 'EOF'
HOPSWORKS_HOST=your-instance.cloud.hopsworks.ai
HOPSWORKS_API_KEY=your-api-key-here
HOPSWORKS_PROJECT=your_project_name
EOF
```

Replace the values with your actual Hopsworks instance details:
- `HOPSWORKS_HOST`: Your Hopsworks instance hostname (without https://)
- `HOPSWORKS_API_KEY`: Your API key from Hopsworks
- `HOPSWORKS_PROJECT`: The name of your project

### 4. Install dotenv (for loading environment variables)

```bash
npm install dotenv
```

## Running the Basic Example

### Option 1: Using ts-node (recommended for development)

Install ts-node to run TypeScript files directly:

```bash
npm install -g ts-node
# or locally
npm install --save-dev ts-node
```

Then run:

```bash
ts-node examples/basic-usage.ts
```

### Option 2: Compile and Run with Node

First, compile the example:

```bash
npx tsc examples/basic-usage.ts --outDir dist/examples --module commonjs --esModuleInterop
```

Then run the compiled JavaScript:

```bash
node dist/examples/basic-usage.js
```

### Option 3: Use npm Scripts (easiest)

I've added an npm script to make running examples easy:

```bash
npm run example
```

This will run the basic-usage example with all the right settings.

## Expected Output

When you run the example successfully, you should see output like:

```
Connecting to Hopsworks...
Getting project...
Connected to project: my_project
Getting feature store...
Connected to feature store: my_project_featurestore
Creating feature group...
Feature group: temperature_readings (version 1)
  - Online enabled: true
  - Primary key: sensor_id, timestamp
Inserting 3 records...
Data inserted successfully!
Connection closed.
```

## Troubleshooting

### "Cannot find module" errors

Make sure you've installed all dependencies:
```bash
npm install
```

### "ts-node: command not found"

Install ts-node:
```bash
npm install --save-dev ts-node
```

Or use the global installation:
```bash
npm install -g ts-node
```

### TypeScript compilation errors

Make sure you've built the project first:
```bash
npm run build
```

### Environment variable not found

Make sure your `.env` file is in the `javascript/` directory and contains all required variables:
```
HOPSWORKS_HOST=your-instance.cloud.hopsworks.ai
HOPSWORKS_API_KEY=your-api-key
HOPSWORKS_PROJECT=your_project
```

### Authentication errors

- Check that your API key is correct and hasn't expired
- Verify the API key has the required scopes (project, featurestore)
- Ensure the host is correct (without `https://`)

## Creating Your Own Example

Create a new file in the `examples/` directory:

```typescript
// examples/my-example.ts
import 'dotenv/config';
import { connection } from '../src';

async function main() {
  const conn = await connection({
    host: process.env.HOPSWORKS_HOST!,
    apiKey: process.env.HOPSWORKS_API_KEY!,
    project: process.env.HOPSWORKS_PROJECT!
  });

  // Your code here
  const project = await conn.getProject();
  console.log(`Working with project: ${project.name}`);

  conn.close();
}

main().catch(console.error);
```

Run it with:
```bash
ts-node examples/my-example.ts
```

## Quick Reference

```bash
# Install dependencies
cd javascript
npm install

# Run the basic example
npm run example

# Build the project
npm run build

# Run a specific example with ts-node
ts-node examples/basic-usage.ts

# Format code
npm run format

# Lint code
npm run lint
```
