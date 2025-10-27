#!/usr/bin/env node

/**
 * ArbFinder CLI (TypeScript/Node.js version)
 * 
 * Command-line interface for interacting with ArbFinder API
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ArbFinderClient, Listing, Statistics } from '@arbfinder/client';
import { table } from 'table';

const version = '0.4.0';

/**
 * Format price for display
 */
function formatPrice(price: number, currency: string = 'USD'): string {
  const symbol = currency === 'USD' ? '$' : currency;
  return `${symbol}${price.toFixed(2)}`;
}

/**
 * Format timestamp for display
 */
function formatTimestamp(ts: number): string {
  return new Date(ts * 1000).toLocaleString();
}

/**
 * Display listings as a table
 */
function displayListings(listings: Listing[]): void {
  if (listings.length === 0) {
    console.log(chalk.yellow('No listings found.'));
    return;
  }

  const data = [
    ['Source', 'Title', 'Price', 'Condition', 'Date'],
    ...listings.map(l => [
      chalk.cyan(l.source),
      l.title.substring(0, 40),
      chalk.green(formatPrice(l.price, l.currency)),
      l.condition,
      formatTimestamp(l.ts),
    ]),
  ];

  console.log(table(data));
}

/**
 * Display statistics
 */
function displayStatistics(stats: Statistics): void {
  console.log(chalk.bold('\n📊 Database Statistics\n'));
  
  const data = [
    ['Metric', 'Value'],
    ['Total Listings', chalk.green(stats.total_listings.toString())],
    ['Unique Sources', chalk.cyan(stats.unique_sources.toString())],
    ['Average Price', chalk.yellow(formatPrice(stats.avg_price))],
    ['Total Comps', chalk.magenta(stats.total_comps.toString())],
  ];

  console.log(table(data));
}

/**
 * Main program
 */
const program = new Command();

program
  .name('arbfinder-ts')
  .description('ArbFinder CLI - Find arbitrage opportunities')
  .version(version);

// Global options
program
  .option('--api-url <url>', 'API base URL', 'http://localhost:8080')
  .option('--timeout <ms>', 'Request timeout in milliseconds', '30000');

/**
 * List command
 */
program
  .command('list')
  .description('List all listings')
  .option('-l, --limit <number>', 'Number of results', '10')
  .option('-o, --offset <number>', 'Offset for pagination', '0')
  .option('-s, --sort <field>', 'Sort by field (ts|price|title)', 'ts')
  .option('--source <source>', 'Filter by source')
  .action(async (options) => {
    const client = new ArbFinderClient({
      baseURL: program.opts().apiUrl,
      timeout: parseInt(program.opts().timeout),
    });

    const spinner = ora('Fetching listings...').start();

    try {
      const response = await client.getListings({
        limit: parseInt(options.limit),
        offset: parseInt(options.offset),
        order_by: options.sort,
        source: options.source,
      });

      spinner.succeed(`Found ${response.total} listings`);
      displayListings(response.data);
      
      if (response.total > response.data.length) {
        console.log(chalk.dim(`\nShowing ${response.data.length} of ${response.total} results`));
      }
    } catch (error: any) {
      spinner.fail('Failed to fetch listings');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

/**
 * Search command
 */
program
  .command('search <query>')
  .description('Search for listings')
  .action(async (query) => {
    const client = new ArbFinderClient({
      baseURL: program.opts().apiUrl,
      timeout: parseInt(program.opts().timeout),
    });

    const spinner = ora(`Searching for "${query}"...`).start();

    try {
      const results = await client.searchListings(query);
      spinner.succeed(`Found ${results.length} results`);
      displayListings(results);
    } catch (error: any) {
      spinner.fail('Search failed');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

/**
 * Stats command
 */
program
  .command('stats')
  .description('Show database statistics')
  .action(async () => {
    const client = new ArbFinderClient({
      baseURL: program.opts().apiUrl,
      timeout: parseInt(program.opts().timeout),
    });

    const spinner = ora('Fetching statistics...').start();

    try {
      const stats = await client.getStatistics();
      spinner.stop();
      displayStatistics(stats);
    } catch (error: any) {
      spinner.fail('Failed to fetch statistics');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

/**
 * Info command
 */
program
  .command('info')
  .description('Get API information')
  .action(async () => {
    const client = new ArbFinderClient({
      baseURL: program.opts().apiUrl,
      timeout: parseInt(program.opts().timeout),
    });

    const spinner = ora('Fetching API info...').start();

    try {
      const info = await client.getInfo();
      spinner.stop();
      console.log(chalk.bold('\n🚀 API Information\n'));
      console.log(JSON.stringify(info, null, 2));
    } catch (error: any) {
      spinner.fail('Failed to fetch API info');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

/**
 * Comps command
 */
program
  .command('comps [query]')
  .description('Get comparable prices')
  .option('-l, --limit <number>', 'Number of results', '10')
  .action(async (query, options) => {
    const client = new ArbFinderClient({
      baseURL: program.opts().apiUrl,
      timeout: parseInt(program.opts().timeout),
    });

    const spinner = ora(query ? `Searching comps for "${query}"...` : 'Fetching comps...').start();

    try {
      const comps = query 
        ? await client.searchComps(query)
        : await client.getComps({ limit: parseInt(options.limit) });

      spinner.succeed(`Found ${comps.length} comparable prices`);

      if (comps.length === 0) {
        console.log(chalk.yellow('No comps found.'));
        return;
      }

      const data = [
        ['Title', 'Avg Price', 'Median Price', 'Count'],
        ...comps.map(c => [
          c.key_title.substring(0, 40),
          chalk.green(formatPrice(c.avg_price)),
          chalk.yellow(formatPrice(c.median_price)),
          chalk.cyan(c.count.toString()),
        ]),
      ];

      console.log(table(data));
    } catch (error: any) {
      spinner.fail('Failed to fetch comps');
      console.error(chalk.red(error.message));
      process.exit(1);
    }
  });

// Parse arguments
program.parse();
