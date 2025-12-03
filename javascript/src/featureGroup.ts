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
import { FeatureGroupData, FeatureGroupApi, Feature } from './api/featureGroupApi';
import { FeatureStore } from './featureStore';

/**
 * Represents a Feature Group in the Feature Store.
 */
export class FeatureGroup {
  public readonly id: number;
  public readonly name: string;
  public readonly version: number;
  public readonly description: string;
  public readonly featurestoreId: number;
  public readonly onlineEnabled: boolean;
  public readonly features: Feature[];
  public readonly primaryKey: string[];
  public readonly partitionKey: string[];
  public readonly eventTime?: string;

  private featureGroupApi: FeatureGroupApi;

  constructor(
    data: FeatureGroupData,
    private client: BaseClient,
    private featureStore: FeatureStore
  ) {
    this.id = data.id;
    this.name = data.name;
    this.version = data.version;
    this.description = data.description;
    this.featurestoreId = data.featurestoreId;
    this.onlineEnabled = data.onlineEnabled;
    this.features = data.features;
    this.primaryKey = data.primaryKey;
    this.partitionKey = data.partitionKey;
    this.eventTime = data.eventTime;

    this.featureGroupApi = new FeatureGroupApi(this.client, this.featurestoreId);
  }

  /**
   * Insert data into the feature group.
   *
   * Persists data to both offline (and online if enabled) feature store.
   * Data is provided as an array of objects where each object represents a row.
   *
   * @param data - Array of objects to insert
   * @param write - Write mode: 'insert' or 'upsert' (default: 'upsert')
   *
   * @example
   * ```typescript
   * const data = [
   *   { id: 1, city: 'Stockholm', temperature: 15.5, date: '2024-01-01' },
   *   { id: 2, city: 'Oslo', temperature: 12.3, date: '2024-01-01' }
   * ];
   *
   * await fg.insert(data);
   * ```
   *
   * @example Upsert mode (update if exists, insert if not)
   * ```typescript
   * await fg.insert(data, 'upsert');
   * ```
   *
   * @example Insert mode (only insert, fail on duplicates)
   * ```typescript
   * await fg.insert(data, 'insert');
   * ```
   */
  async insert(data: Record<string, any>[], write: 'insert' | 'upsert' = 'upsert'): Promise<void> {
    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('Data must be a non-empty array of objects');
    }

    // Validate that all rows have the same keys
    const firstRowKeys = Object.keys(data[0]).sort();
    for (let i = 1; i < data.length; i++) {
      const rowKeys = Object.keys(data[i]).sort();
      if (JSON.stringify(firstRowKeys) !== JSON.stringify(rowKeys)) {
        throw new Error('All rows must have the same set of keys');
      }
    }

    await this.featureGroupApi.insertData(this.id, data, write);
  }

  /**
   * Save data to the feature group.
   * Alias for insert() with 'upsert' mode.
   *
   * @param data - Array of objects to save
   */
  async save(data: Record<string, any>[]): Promise<void> {
    await this.insert(data, 'upsert');
  }

  toString(): string {
    return `FeatureGroup(${this.name}, version=${this.version}, onlineEnabled=${this.onlineEnabled})`;
  }
}
