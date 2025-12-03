# Hopsworks JavaScript API

JavaScript/TypeScript client library for the Hopsworks Feature Store.

## Features

This is a limited initial version of the JavaScript API that provides:

- ✅ Connection to Hopsworks using API keys
- ✅ Project access
- ✅ Feature Store access
- ✅ Feature Group creation and retrieval
- ✅ Writing data to online-enabled feature groups

## Installation

```bash
npm install @hopsworks/api
```

## Quick Start

```typescript
import { connection } from '@hopsworks/api';

// Connect to Hopsworks
const conn = await connection({
  host: 'my-instance.cloud.hopsworks.ai',
  apiKey: 'your-api-key',
  project: 'my_project'
});

// Get project and feature store
const project = await conn.getProject();
const fs = await project.getFeatureStore();

// Get or create a feature group
const fg = await fs.getOrCreateFeatureGroup('prices', 1, {
  primaryKey: ['id'],
  eventTime: 'timestamp',
  onlineEnabled: true,
  description: 'Price data'
});

// Insert data
const data = [
  { id: 1, price: 100.5, timestamp: '2024-01-01T00:00:00Z' },
  { id: 2, price: 101.2, timestamp: '2024-01-01T01:00:00Z' }
];

await fg.insert(data);
```

## API Documentation

### Connection

Create a connection to Hopsworks:

```typescript
import { connection } from '@hopsworks/api';

const conn = await connection({
  host: 'my-instance.cloud.hopsworks.ai',
  port: 443,                                    // optional, defaults to 443
  apiKey: 'your-api-key',
  hostnameVerification: true,                   // optional, defaults to true
  project: 'my_project'                         // optional
});
```

#### Connection Methods

- `getProject(name?: string)` - Get a project by name
- `getProjects()` - Get all accessible projects
- `projectExists(name: string)` - Check if a project exists
- `close()` - Close the connection

### Project

```typescript
const project = await conn.getProject('my_project');

// Get feature store
const fs = await project.getFeatureStore();
```

### Feature Store

```typescript
const fs = await project.getFeatureStore();

// Get an existing feature group
const fg = await fs.getFeatureGroup('my_feature_group', 1);

// Create a new feature group
const newFg = await fs.createFeatureGroup('new_fg', {
  version: 1,
  description: 'My feature group',
  primaryKey: ['id'],
  eventTime: 'timestamp',
  onlineEnabled: true
});

// Get or create (idempotent)
const fg = await fs.getOrCreateFeatureGroup('my_fg', 1, {
  primaryKey: ['id'],
  onlineEnabled: true
});
```

### Feature Group

```typescript
// Insert data (upsert mode - updates existing or inserts new)
await fg.insert([
  { id: 1, value: 100 },
  { id: 2, value: 200 }
]);

// Insert mode (fails on duplicates)
await fg.insert(data, 'insert');

// Upsert mode (default)
await fg.insert(data, 'upsert');

// Save is an alias for insert with upsert mode
await fg.save(data);
```

## Development

### Setup

```bash
cd javascript
npm install
```

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

## Limitations

This is an initial version with limited functionality. The following features are not yet implemented:

- Reading data from feature groups
- Feature views
- Training datasets
- Model registry
- Model serving
- Statistics and data validation
- Transformation functions
- External feature groups
- And many other features available in the Python API

## Requirements

- Node.js >= 16.0.0
- Hopsworks instance (cloud or on-premise)
- Valid Hopsworks API key

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please see the main repository's CONTRIBUTING.md for guidelines.

## Support

- [Hopsworks Documentation](https://docs.hopsworks.ai)
- [Community Forum](https://community.hopsworks.ai)
- [GitHub Issues](https://github.com/logicalclocks/hopsworks-api/issues)

## Authors

Hopsworks AB

## Changelog

### 0.1.0 (Initial Release)

- Basic connection and authentication
- Project access
- Feature Store access
- Feature Group creation and data insertion
- Support for online-enabled feature groups
