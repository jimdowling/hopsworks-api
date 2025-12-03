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

import { BaseClient } from './client/base';
import { FeatureStoreData } from './api/featureStoreApi';
import { FeatureGroup } from './featureGroup';
import { FeatureGroupApi } from './api/featureGroupApi';

/**
 * Feature Store class used to manage feature store entities, like feature groups.
 */
export class FeatureStore {
  public readonly id: number;
  public readonly name: string;
  public readonly projectName: string;
  public readonly projectId: number;
  public readonly onlineEnabled: boolean;
  public readonly offlineFeaturestoreName: string;
  public readonly onlineFeaturestoreName?: string;

  private featureGroupApi: FeatureGroupApi;

  constructor(data: FeatureStoreData, private client: BaseClient) {
    this.id = data.featurestoreId;
    this.name = data.featurestoreName;
    this.projectName = data.projectName;
    this.projectId = data.projectId;
    this.onlineEnabled = data.onlineEnabled;
    this.offlineFeaturestoreName = data.offlineFeaturestoreName;
    this.onlineFeaturestoreName = data.onlineFeaturestoreName;

    this.featureGroupApi = new FeatureGroupApi(this.client, this.id);
  }

  /**
   * Get a feature group entity from the feature store.
   *
   * @param name - Name of the feature group to get
   * @param version - Version of the feature group (defaults to 1)
   * @returns A FeatureGroup object
   *
   * @example
   * ```typescript
   * const fg = await fs.getFeatureGroup('electricity_prices', 1);
   * ```
   */
  async getFeatureGroup(name: string, version: number = 1): Promise<FeatureGroup> {
    const fgData = await this.featureGroupApi.get(name, version);
    return new FeatureGroup(fgData, this.client, this);
  }

  /**
   * Get or create a feature group metadata object.
   *
   * @param name - Name of the feature group
   * @param version - Version of the feature group
   * @param options - Feature group configuration options
   * @returns A FeatureGroup object
   *
   * @example
   * ```typescript
   * const fg = await fs.getOrCreateFeatureGroup('prices', 1, {
   *   primaryKey: ['id'],
   *   onlineEnabled: true,
   *   description: 'Price data'
   * });
   * ```
   */
  async getOrCreateFeatureGroup(
    name: string,
    version: number,
    options: {
      description?: string;
      primaryKey?: string[];
      eventTime?: string;
      onlineEnabled?: boolean;
    } = {}
  ): Promise<FeatureGroup> {
    try {
      return await this.getFeatureGroup(name, version);
    } catch (error) {
      return await this.createFeatureGroup(name, options);
    }
  }

  /**
   * Create a feature group metadata object.
   *
   * Note: This method is lazy and does not persist any metadata or feature data.
   * To persist the feature group and save feature data, call the insert() method
   * with your data.
   *
   * @param name - Name of the feature group to create
   * @param options - Feature group configuration options
   * @returns A FeatureGroup object
   *
   * @example
   * ```typescript
   * const fg = await fs.createFeatureGroup('air_quality', {
   *   description: 'Air Quality characteristics',
   *   version: 1,
   *   primaryKey: ['city', 'date'],
   *   eventTime: 'date',
   *   onlineEnabled: true
   * });
   *
   * // Later, insert data
   * await fg.insert(data);
   * ```
   */
  async createFeatureGroup(
    name: string,
    options: {
      version?: number;
      description?: string;
      primaryKey?: string[];
      eventTime?: string;
      onlineEnabled?: boolean;
      partitionKey?: string[];
    } = {}
  ): Promise<FeatureGroup> {
    const fgData = await this.featureGroupApi.create(name, {
      version: options.version,
      description: options.description || '',
      primaryKey: options.primaryKey || [],
      eventTime: options.eventTime,
      onlineEnabled: options.onlineEnabled || false,
      partitionKey: options.partitionKey || [],
      featurestoreId: this.id,
    });

    return new FeatureGroup(fgData, this.client, this);
  }
}
