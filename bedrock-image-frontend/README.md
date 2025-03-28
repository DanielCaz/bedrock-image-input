# Create PID App

A CLI tool to quickly scaffold a modern React application with an opinionated setup for productivity and developer experience.

## Features

The generated application comes pre-configured with:

- ⚡ [Vite](https://vitejs.dev/) - Next generation frontend tooling
- ⚛️ [React](https://react.dev/) with TypeScript
- 🧭 [TanStack Router](https://tanstack.com/router) - Type-safe routing
- 🔄 [TanStack Query](https://tanstack.com/query) - Data fetching and caching
- 🎨 [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- 🌼 [DaisyUI](https://daisyui.com/) - Tailwind CSS component library
- 🧹 [Prettier](https://prettier.io/) with Tailwind plugin - Code formatting
- 👨‍💻 VS Code configurations and recommended extensions

## Requirements

- [Bun](https://bun.sh/) (latest version)
- [VS Code](https://code.visualstudio.com/) (recommended)

## Installation

```bash
# Install globally
bun add -g @compucloud-mx/create-pid-app

# Or use directly with bunx
bunx @compucloud-mx/create-pid-app
```

## Usage

```bash
# Run the CLI
create-pid-app

# Or use with bunx
bunx @compucloud-mx/create-pid-app
```

Follow the interactive prompts:

1. Enter your project name
2. Choose whether to initialize a git repository
3. Choose whether to open the project in VS Code

The CLI will:

1. Create a new Vite + React + TypeScript project
2. Install and configure all dependencies
3. Set up routing with TanStack Router
4. Configure Tailwind CSS with DaisyUI
5. Set up Prettier with Tailwind plugin
6. Configure VS Code settings and recommended extensions
7. Initialize a git repository (if selected)
8. Open the project in VS Code (if selected)

## Project Structure

```
my-pid-app/
├── node_modules/
├── public/
├── src/
│   ├── routes/
│   │   ├── __root.tsx
│   │   └── index.tsx
│   ├── index.css
│   ├── main.tsx
│   └── routeTree.gen.ts (generated)
├── .vscode/
│   ├── settings.json
│   └── extensions.json
├── .gitignore
├── .prettierrc
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```
