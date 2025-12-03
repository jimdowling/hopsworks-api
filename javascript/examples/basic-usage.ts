/**
 * Basic usage example for Hopsworks JavaScript API
 *
 * This example demonstrates:
 * 1. Connecting to Hopsworks
 * 2. Accessing a project and feature store
 * 3. Creating a feature group
 * 4. Inserting data
 */

import 'dotenv/config';
import { connection } from '../src';

async function main() {
  // 1. Connect to Hopsworks
  console.log('Connecting to Hopsworks...');
  const conn = await connection({
    host: process.env.HOPSWORKS_HOST || 'my-instance.cloud.hopsworks.ai',
    apiKey: process.env.HOPSWORKS_API_KEY || 'your-api-key',
    project: process.env.HOPSWORKS_PROJECT || 'my_project',
  });

  // 2. Get project and feature store
  console.log('Getting project...');
  const project = await conn.getProject();
  console.log(`Connected to project: ${project.name}`);

  console.log('Getting feature store...');
  const fs = await project.getFeatureStore();
  console.log(`Connected to feature store: ${fs.name}`);

  // 3. Create or get a feature group
  console.log('Creating feature group...');
  const fg = await fs.getOrCreateFeatureGroup('temperature_readings', 1, {
    description: 'Temperature sensor readings',
    primaryKey: ['sensor_id', 'timestamp'],
    eventTime: 'timestamp',
    onlineEnabled: true,
  });

  console.log(`Feature group: ${fg.name} (version ${fg.version})`);
  console.log(`  - Online enabled: ${fg.onlineEnabled}`);
  console.log(`  - Primary key: ${fg.primaryKey.join(', ')}`);

  // 4. Prepare sample data
  const now = new Date();
  const data = [
    {
      sensor_id: 'sensor_001',
      timestamp: now.toISOString(),
      temperature: 22.5,
      humidity: 65.0,
      location: 'Stockholm',
    },
    {
      sensor_id: 'sensor_002',
      timestamp: now.toISOString(),
      temperature: 18.3,
      humidity: 70.5,
      location: 'Oslo',
    },
    {
      sensor_id: 'sensor_003',
      timestamp: now.toISOString(),
      temperature: 20.1,
      humidity: 68.2,
      location: 'Copenhagen',
    },
  ];

  // 5. Insert data
  console.log(`Inserting ${data.length} records...`);
  await fg.insert(data);
  console.log('Data inserted successfully!');

  // 6. Close connection
  conn.close();
  console.log('Connection closed.');
}

// Run the example
main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
