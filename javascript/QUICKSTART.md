# Quick Start Guide - Hopsworks JavaScript API

This guide will help you get started with the Hopsworks JavaScript API in just a few minutes.

## Prerequisites

- Node.js >= 16.0.0
- A Hopsworks instance (cloud or on-premise)
- A valid Hopsworks API key

### Getting a Hopsworks API Key

1. Log in to your Hopsworks instance
2. Navigate to your profile settings
3. Go to "API Keys"
4. Click "Create new API Key"
5. Give it a name and select the scopes you need (at minimum: "project", "featurestore")
6. Copy the generated API key (you won't be able to see it again!)

## Installation

```bash
npm install @logicalclocks/hopsworks-api
```

## Your First Feature Group

### Step 1: Connect to Hopsworks

Create a new file `example.ts`:

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  // Connect to Hopsworks
  const conn = await connection({
    host: 'my-instance.cloud.hopsworks.ai',
    apiKey: 'your-api-key-here',
    project: 'my_project'
  });

  console.log('Connected to Hopsworks!');
}

main().catch(console.error);
```

### Step 2: Access Your Feature Store

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  const conn = await connection({
    host: 'my-instance.cloud.hopsworks.ai',
    apiKey: 'your-api-key-here',
    project: 'my_project'
  });

  // Get your project
  const project = await conn.getProject();
  console.log(`Project: ${project.name}`);

  // Get the feature store
  const fs = await project.getFeatureStore();
  console.log(`Feature Store: ${fs.name}`);
}

main().catch(console.error);
```

### Step 3: Create a Feature Group

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  const conn = await connection({
    host: 'my-instance.cloud.hopsworks.ai',
    apiKey: 'your-api-key-here',
    project: 'my_project'
  });

  const project = await conn.getProject();
  const fs = await project.getFeatureStore();

  // Create a feature group for sensor data
  const fg = await fs.getOrCreateFeatureGroup('sensor_data', 1, {
    description: 'Temperature and humidity readings from IoT sensors',
    primaryKey: ['sensor_id', 'timestamp'],
    eventTime: 'timestamp',
    onlineEnabled: true
  });

  console.log(`Feature Group: ${fg.name} (version ${fg.version})`);
  console.log(`Online enabled: ${fg.onlineEnabled}`);
}

main().catch(console.error);
```

### Step 4: Insert Data

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  const conn = await connection({
    host: 'my-instance.cloud.hopsworks.ai',
    apiKey: 'your-api-key-here',
    project: 'my_project'
  });

  const project = await conn.getProject();
  const fs = await project.getFeatureStore();
  const fg = await fs.getFeatureGroup('sensor_data', 1);

  // Prepare your data
  const data = [
    {
      sensor_id: 'sensor_001',
      timestamp: new Date().toISOString(),
      temperature: 22.5,
      humidity: 65.0,
      location: 'Room A'
    },
    {
      sensor_id: 'sensor_002',
      timestamp: new Date().toISOString(),
      temperature: 21.8,
      humidity: 68.5,
      location: 'Room B'
    }
  ];

  // Insert the data
  await fg.insert(data);
  console.log('Data inserted successfully!');

  // Clean up
  conn.close();
}

main().catch(console.error);
```

## Using Environment Variables

For better security, use environment variables for your credentials:

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  const conn = await connection({
    host: process.env.HOPSWORKS_HOST!,
    apiKey: process.env.HOPSWORKS_API_KEY!,
    project: process.env.HOPSWORKS_PROJECT!
  });

  // Your code here...
}

main().catch(console.error);
```

Create a `.env` file:
```
HOPSWORKS_HOST=my-instance.cloud.hopsworks.ai
HOPSWORKS_API_KEY=your-api-key-here
HOPSWORKS_PROJECT=my_project
```

And load it using a package like `dotenv`:
```bash
npm install dotenv
```

```typescript
import 'dotenv/config';
import { connection } from '@logicalclocks/hopsworks-api';
// ... rest of your code
```

## Complete Example

Here's a complete working example that demonstrates all the basic features:

```typescript
import { connection } from '@logicalclocks/hopsworks-api';

async function main() {
  console.log('🚀 Starting Hopsworks example...\n');

  // 1. Connect
  console.log('📡 Connecting to Hopsworks...');
  const conn = await connection({
    host: process.env.HOPSWORKS_HOST!,
    apiKey: process.env.HOPSWORKS_API_KEY!,
    project: process.env.HOPSWORKS_PROJECT!
  });

  // 2. Get project
  console.log('📁 Getting project...');
  const project = await conn.getProject();
  console.log(`   ✓ Project: ${project.name}\n`);

  // 3. Get feature store
  console.log('🗄️  Getting feature store...');
  const fs = await project.getFeatureStore();
  console.log(`   ✓ Feature Store: ${fs.name}\n`);

  // 4. Create/get feature group
  console.log('📊 Creating feature group...');
  const fg = await fs.getOrCreateFeatureGroup('weather_data', 1, {
    description: 'Weather measurements',
    primaryKey: ['city', 'timestamp'],
    eventTime: 'timestamp',
    onlineEnabled: true
  });
  console.log(`   ✓ Feature Group: ${fg.name} v${fg.version}`);
  console.log(`   ✓ Online: ${fg.onlineEnabled}\n`);

  // 5. Prepare and insert data
  console.log('💾 Inserting data...');
  const now = new Date().toISOString();
  const data = [
    { city: 'Stockholm', timestamp: now, temperature: 15.5, humidity: 72 },
    { city: 'Oslo', timestamp: now, temperature: 12.3, humidity: 78 },
    { city: 'Copenhagen', timestamp: now, temperature: 14.1, humidity: 75 }
  ];

  await fg.insert(data);
  console.log(`   ✓ Inserted ${data.length} records\n`);

  // 6. Done
  console.log('✅ All done!');
  conn.close();
}

main().catch((error) => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
```

## Next Steps

- Read the full [README](./README.md) for more details
- Check out the [examples](./examples/) directory
- Review the [API documentation](./src/index.ts)

## Common Issues

### "Project not found"
- Ensure your API key has access to the project
- Check that the project name is spelled correctly

### "Authentication failed"
- Verify your API key is correct
- Check that your API key hasn't expired
- Ensure your API key has the required scopes

### "Feature group not found"
- Use `getOrCreateFeatureGroup()` instead of `getFeatureGroup()` for a new feature group
- Check the feature group name and version

## Support

- [Hopsworks Documentation](https://docs.hopsworks.ai)
- [Community Forum](https://community.hopsworks.ai)
- [GitHub Issues](https://github.com/logicalclocks/hopsworks-api/issues)
