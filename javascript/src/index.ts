/**
 * Copyright 2024 Hopsworks AB
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Main exports
export { Connection, connection, ConnectionOptions } from './connection';
export { Project } from './project';
export { FeatureStore } from './featureStore';
export { FeatureGroup } from './featureGroup';

// Type exports
export type { ProjectData } from './api/projectApi';
export type { FeatureStoreData } from './api/featureStoreApi';
export type { FeatureGroupData, Feature } from './api/featureGroupApi';

// Error exports
export { RestAPIError } from './client/base';
