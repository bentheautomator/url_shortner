#!/usr/bin/env node

import { program } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import clipboardy from 'clipboardy';
import fetch from 'node-fetch';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

const CONFIG_PATH = join(homedir(), '.shrtnr');
const DEFAULT_API = process.env.SHRTNR_API_URL || 'https://short.automatorprojects.space';

// Load config
function loadConfig() {
  if (existsSync(CONFIG_PATH)) {
    try {
      return JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
    } catch {
      return {};
    }
  }
  return {};
}

// Save config
function saveConfig(config) {
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

// Get API URL
function getApiUrl() {
  const config = loadConfig();
  return config.apiUrl || DEFAULT_API;
}

// ASCII art logo
const logo = chalk.cyan(`
  ███████╗██╗  ██╗██████╗ ████████╗███╗   ██╗██████╗
  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝████╗  ██║██╔══██╗
  ███████╗███████║██████╔╝   ██║   ██╔██╗ ██║██████╔╝
  ╚════██║██╔══██║██╔══██╗   ██║   ██║╚██╗██║██╔══██╗
  ███████║██║  ██║██║  ██║   ██║   ██║ ╚████║██║  ██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
`);

program
  .name('shrtnr')
  .description('CLI for SHRTNR - the badass URL shortener')
  .version('1.0.0');

// Shorten command (default)
program
  .argument('[url]', 'URL to shorten')
  .option('-c, --custom <code>', 'Custom short code')
  .option('-k, --api-key <key>', 'API key for authentication')
  .option('--no-copy', 'Don\'t copy to clipboard')
  .action(async (url, options) => {
    if (!url) {
      console.log(logo);
      program.help();
      return;
    }

    const spinner = ora('Shortening URL...').start();

    try {
      const apiUrl = getApiUrl();
      const config = loadConfig();
      const apiKey = options.apiKey || config.apiKey;

      const headers = {
        'Content-Type': 'application/json'
      };

      if (apiKey) {
        headers['X-API-Key'] = apiKey;
      }

      const response = await fetch(`${apiUrl}/api/shorten`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          url: url,
          custom_code: options.custom || null
        })
      });

      const data = await response.json();

      if (!response.ok) {
        spinner.fail(chalk.red(data.detail || 'Failed to shorten URL'));
        process.exit(1);
      }

      spinner.succeed(chalk.green('URL shortened!'));

      console.log('');
      console.log(chalk.gray('Original:  ') + chalk.white(url));
      console.log(chalk.gray('Short URL: ') + chalk.cyan.bold(data.short_url));
      console.log('');

      if (options.copy !== false) {
        await clipboardy.write(data.short_url);
        console.log(chalk.gray('Copied to clipboard!'));
      }

    } catch (error) {
      spinner.fail(chalk.red('Failed to connect to SHRTNR API'));
      console.log(chalk.gray(`API URL: ${getApiUrl()}`));
      console.log(chalk.gray('Make sure the server is running.'));
      process.exit(1);
    }
  });

// Config command
program
  .command('config')
  .description('Configure SHRTNR CLI')
  .option('--api-url <url>', 'Set API URL')
  .option('--api-key <key>', 'Set default API key')
  .option('--show', 'Show current config')
  .action((options) => {
    const config = loadConfig();

    if (options.show) {
      console.log(logo);
      console.log(chalk.gray('Current configuration:'));
      console.log(chalk.gray('API URL: ') + chalk.cyan(config.apiUrl || DEFAULT_API));
      console.log(chalk.gray('API Key: ') + chalk.cyan(config.apiKey ? '***' + config.apiKey.slice(-4) : 'Not set'));
      return;
    }

    if (options.apiUrl) {
      config.apiUrl = options.apiUrl;
    }

    if (options.apiKey) {
      config.apiKey = options.apiKey;
    }

    saveConfig(config);
    console.log(chalk.green('Configuration saved!'));
  });

// Stats command
program
  .command('stats [code]')
  .description('Get stats for a short URL')
  .action(async (code) => {
    const spinner = ora('Fetching stats...').start();

    try {
      const apiUrl = getApiUrl();

      if (code) {
        // Get specific URL stats
        const response = await fetch(`${apiUrl}/api/urls/${code}`);
        const data = await response.json();

        if (!response.ok) {
          spinner.fail(chalk.red(data.detail || 'URL not found'));
          process.exit(1);
        }

        spinner.succeed(chalk.green('Stats retrieved!'));
        console.log('');
        console.log(chalk.gray('Short Code: ') + chalk.cyan(`/${data.short_code}`));
        console.log(chalk.gray('Clicks:     ') + chalk.yellow.bold(data.click_count));
        console.log(chalk.gray('Created:    ') + chalk.white(new Date(data.created_at).toLocaleDateString()));

        if (data.top_referers && data.top_referers.length > 0) {
          console.log('');
          console.log(chalk.gray('Top Referrers:'));
          data.top_referers.forEach((ref, i) => {
            console.log(chalk.gray(`  ${i + 1}. `) + chalk.white(ref.referer) + chalk.gray(` (${ref.count})`));
          });
        }
      } else {
        // Get global stats
        const response = await fetch(`${apiUrl}/api/stats`);
        const data = await response.json();

        spinner.succeed(chalk.green('Global stats retrieved!'));
        console.log('');
        console.log(chalk.cyan.bold('SHRTNR Global Stats'));
        console.log(chalk.gray('─'.repeat(30)));
        console.log(chalk.gray('Total URLs:    ') + chalk.yellow.bold(data.total_urls));
        console.log(chalk.gray('Total Clicks:  ') + chalk.yellow.bold(data.total_clicks));
        console.log(chalk.gray('URLs Today:    ') + chalk.green(data.urls_today));
        console.log(chalk.gray('Clicks Today:  ') + chalk.green(data.clicks_today));
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to fetch stats'));
      process.exit(1);
    }
  });

// List command
program
  .command('list')
  .description('List your shortened URLs')
  .option('-l, --limit <n>', 'Number of URLs to show', '10')
  .action(async (options) => {
    const spinner = ora('Fetching URLs...').start();

    try {
      const apiUrl = getApiUrl();
      const config = loadConfig();

      const headers = {};
      if (config.apiKey) {
        headers['X-API-Key'] = config.apiKey;
      }

      const response = await fetch(`${apiUrl}/api/urls?limit=${options.limit}`, { headers });
      const data = await response.json();

      spinner.succeed(chalk.green(`Found ${data.length} URLs`));
      console.log('');

      if (data.length === 0) {
        console.log(chalk.gray('No URLs found. Create one with: shrtnr <url>'));
        return;
      }

      data.forEach((url, i) => {
        console.log(
          chalk.gray(`${i + 1}. `) +
          chalk.cyan(`/${url.short_code}`) +
          chalk.gray(' → ') +
          chalk.white(url.original_url.substring(0, 40) + (url.original_url.length > 40 ? '...' : '')) +
          chalk.gray(` (${url.click_count} clicks)`)
        );
      });
    } catch (error) {
      spinner.fail(chalk.red('Failed to fetch URLs'));
      process.exit(1);
    }
  });

program.parse();
