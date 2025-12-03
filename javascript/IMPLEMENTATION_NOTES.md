# Hopsworks JavaScript API - Implementation Notes

## Overview

This is the initial JavaScript/TypeScript implementation of the Hopsworks API, providing a limited but functional subset of the Python API's capabilities.

## Architecture

The JavaScript API follows the same architectural patterns as the Python API:

### Core Components

1. **Client Layer** (`src/client/`)
   - `base.ts`: BaseClient with HTTP request handling using Axios
   - `auth.ts`: Authentication classes (ApiKeyAuth, BearerAuth)

2. **API Layer** (`src/api/`)
   - `projectApi.ts`: Project-related API calls
   - `featureStoreApi.ts`: Feature Store API calls
   - `featureGroupApi.ts`: Feature Group API calls with data ingestion

3. **Domain Layer** (`src/`)
   - `connection.ts`: Main entry point, handles connection lifecycle
   - `project.ts`: Project representation
   - `featureStore.ts`: Feature Store representation
   - `featureGroup.ts`: Feature Group representation with insert functionality

## Implemented Features

### ✅ Connection & Authentication
- API key-based authentication
- Hostname verification control
- Connection lifecycle management

### ✅ Project Access
- Get project by name
- List all projects
- Check project existence

### ✅ Feature Store Access
- Get feature store for a project
- Automatic feature store name resolution

### ✅ Feature Groups
- Get existing feature group
- Create new feature group
- Get or create (idempotent operation)
- **Insert data to online-enabled feature groups**
- Support for both 'insert' and 'upsert' write modes

## Key Design Decisions

### TypeScript
- Full TypeScript implementation for type safety
- Comprehensive type definitions for all data structures
- Async/await pattern throughout

### HTTP Client
- Axios for HTTP requests (similar to Python's requests library)
- Interceptor-based authentication
- Centralized error handling with RestAPIError

### API Compatibility
- Method names and signatures mirror the Python API where possible
- Similar patterns for lazy operations (e.g., createFeatureGroup doesn't persist until insert)
- Consistent parameter naming (camelCase in JS, snake_case in Python API calls)

## Data Flow

### Writing to a Feature Group

```
User Code
    ↓
FeatureGroup.insert(data)
    ↓
FeatureGroupApi.insertData(featureGroupId, data, writeMode)
    ↓
BaseClient.sendRequest('POST', [...path...], { data: payload })
    ↓
Axios HTTP Client (with auth interceptor)
    ↓
Hopsworks REST API
    ↓
Feature Store (Offline + Online if enabled)
```

## REST API Endpoints Used

- `GET /hopsworks-api/api/project/getProjectInfo/{name}` - Get project
- `GET /hopsworks-api/api/project` - List projects
- `GET /hopsworks-api/api/project/{name}/featurestores/{fsName}` - Get feature store
- `GET /hopsworks-api/api/project/{name}/featurestores/{fsId}/featuregroups/{fgName}` - Get feature group
- `POST /hopsworks-api/api/project/{name}/featurestores/{fsId}/featuregroups` - Create feature group
- `POST /hopsworks-api/api/project/{name}/featurestores/{fsId}/featuregroups/{fgId}/ingestion` - Insert data

## Limitations & Future Work

### Not Implemented
- Reading data from feature groups
- Feature views
- Training datasets
- Model registry and serving
- Statistics computation
- Data validation (Great Expectations)
- Transformation functions
- External feature groups
- Streaming ingestion
- Time travel queries
- Point-in-time joins
- Storage connectors
- Tags and metadata management

### Technical Debt
- No comprehensive test suite yet
- Limited error handling and validation
- No retry logic for failed requests
- No connection pooling optimization
- Schema inference not implemented (must match existing schema)

### Known Issues
- Feature creation requires schema to be inferred or provided
- No validation of data against feature group schema before insert
- Limited type checking for feature data types

## Testing Recommendations

1. **Unit Tests**: Test each API class independently with mocked HTTP client
2. **Integration Tests**: Test against a real or mock Hopsworks instance
3. **Example Tests**: Ensure all examples run successfully

## Usage Example

```typescript
import { connection } from '@hopsworks/api';

const conn = await connection({
  host: 'my-instance.cloud.hopsworks.ai',
  apiKey: process.env.HOPSWORKS_API_KEY,
  project: 'my_project'
});

const project = await conn.getProject();
const fs = await project.getFeatureStore();

const fg = await fs.getOrCreateFeatureGroup('prices', 1, {
  primaryKey: ['id'],
  eventTime: 'timestamp',
  onlineEnabled: true
});

await fg.insert([
  { id: 1, price: 100.5, timestamp: new Date().toISOString() }
]);
```

## Contributing

When extending this API:

1. Follow the existing architectural patterns
2. Mirror the Python API structure where applicable
3. Add comprehensive JSDoc comments
4. Include examples in the README
5. Update this document with new features

## Version History

- **0.1.0** (Initial Release)
  - Basic connection and authentication
  - Project and feature store access
  - Feature group creation and data insertion
  - Support for online-enabled feature groups
