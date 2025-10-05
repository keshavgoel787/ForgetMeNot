# ForgetMeNot Frontend - React + TypeScript + Vite

Properly structured React application following best practices for component separation and maintainability.

## 📁 Project Structure

```
client_frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   ├── HomeScreen.tsx   # Dashboard with orbit visualization
│   │   ├── RememberScreen.tsx   # Memory input and management
│   │   └── MyMemoriesScreen.tsx # Memory gallery
│   ├── styles/              # CSS modules
│   │   ├── App.css          # Global app styles
│   │   ├── Sidebar.css      # Sidebar-specific styles
│   │   ├── HomeScreen.css   # Dashboard styles
│   │   └── RememberScreen.css  # Remember screen styles
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # Shared types
│   ├── assets/              # Images, icons, fonts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
└── vite.config.ts           # Vite config
```

## 🎨 Architecture

### Component Separation

**✅ Proper Structure:**
- Each component in its own file
- Styles separated from logic
- TypeScript interfaces for type safety
- Clear component hierarchy

**❌ Old Structure (test.html):**
- Everything in one HTML file
- Inline CSS and JavaScript
- No type checking
- Difficult to maintain

### Component Overview

#### **Sidebar.tsx**
- Navigation component
- Screen switching logic
- Active state management

#### **HomeScreen.tsx**
- Dashboard view
- Orbit visualization of categories
- Welcome cards

#### **RememberScreen.tsx**
- Memory input form
- Memory grid display
- Suggestion system
- State management for memories

#### **MyMemoriesScreen.tsx**
- Memory collection view
- Card-based layout
- Future: Memory details and editing

## 🚀 Running the App

### Development Server

```bash
cd client_frontend
npm install
npm run dev
```

Opens at: http://localhost:5173/

### Build for Production

```bash
npm run build
```

Output in `dist/` directory

### Preview Production Build

```bash
npm run preview
```

## 🔧 Development Commands

```bash
# Install dependencies
npm install

# Start dev server (hot reload)
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Type check
npx tsc --noEmit
```

## 📦 Key Technologies

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **CSS Modules** - Scoped styling

## 🎯 Best Practices Implemented

### ✅ Component Design
- Single responsibility principle
- Props interface definitions
- Functional components with hooks
- Clear naming conventions

### ✅ File Organization
- Components separated by feature
- Styles co-located with components
- Shared types in dedicated folder
- Assets in separate directory

### ✅ TypeScript Usage
- Strict mode enabled
- Type definitions for all props
- Interface exports for reusability
- No `any` types

### ✅ State Management
- React hooks (useState)
- Props drilling for simplicity
- Type-safe state updates
- Clear state ownership

## 🔄 Migrating from test.html

### What Changed:

**Before (test.html):**
```html
<script type="text/babel">
  function App() {
    // All code in one file
  }
</script>
```

**After (App.tsx):**
```typescript
import { useState } from 'react';
import Sidebar from './components/Sidebar';
// Clean, modular imports
```

### Benefits:

1. **Type Safety** - TypeScript catches errors at compile time
2. **Hot Reload** - Instant updates without refresh
3. **Code Splitting** - Faster load times
4. **Maintainability** - Easy to find and update code
5. **Scalability** - Add features without mess
6. **Debugging** - Better error messages and stack traces

## 📝 Adding New Features

### Add a New Screen

1. Create component file:
```typescript
// src/components/NewScreen.tsx
import React from 'react';
import '../styles/NewScreen.css';

const NewScreen: React.FC = () => {
  return (
    <div className="screen active">
      <div className="header-bar">New Screen</div>
      <div className="content">
        {/* Your content */}
      </div>
    </div>
  );
};

export default NewScreen;
```

2. Create styles:
```css
/* src/styles/NewScreen.css */
.new-screen-specific {
  /* Your styles */
}
```

3. Update types:
```typescript
// src/types/index.ts
export type Screen = 'dashboard' | 'remember' | 'My_Memories' | 'newScreen';
```

4. Import and use in App.tsx:
```typescript
import NewScreen from './components/NewScreen';

// Add to switch statement
case 'newScreen':
  return <NewScreen />;
```

5. Add navigation button in Sidebar.tsx

### Add Assets (Images)

1. Place images in `src/assets/`
2. Import in component:
```typescript
import logo from '../assets/logo.png';

// Use in JSX:
<img src={logo} alt="Logo" />
```

## 🐛 Common Issues

### Issue: Import errors
**Solution:** Ensure file extensions are correct (.tsx for components)

### Issue: Style not applying
**Solution:** Import CSS file in component

### Issue: Type errors
**Solution:** Run `npx tsc --noEmit` to see all type errors

### Issue: Hot reload not working
**Solution:** Restart dev server with `npm run dev`

## 🔗 Useful Resources

- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [React + TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

## 🎨 Styling Guide

### CSS Best Practices

- Use descriptive class names
- Follow BEM naming convention
- Keep specificity low
- Use CSS variables for theming
- Group related styles together

### Example:
```css
/* Component styles */
.sidebar {
  /* Layout */
  display: flex;
  flex-direction: column;
  
  /* Spacing */
  padding: 16px;
  gap: 12px;
  
  /* Visual */
  background: #a9bff0;
  border-radius: 8px;
}

.sidebar__item {
  /* Child element styles */
}

.sidebar__item--active {
  /* Modifier styles */
}
```

## 🚀 Next Steps

Future improvements:

1. **State Management** - Add Context API or Zustand
2. **Routing** - Implement React Router
3. **API Integration** - Connect to backend endpoints
4. **Testing** - Add Jest + React Testing Library
5. **Animations** - Add Framer Motion
6. **Forms** - Implement React Hook Form
7. **Assets** - Add actual images to `src/assets/`

## 📊 Performance Tips

- Lazy load components with `React.lazy()`
- Memoize expensive computations with `useMemo`
- Prevent unnecessary re-renders with `React.memo`
- Use production build for deployment
- Optimize images and assets

---

**Built with ❤️ using modern React best practices**
