---
name: frontend-pages-components
description: Build frontend pages, reusable components, layouts, and styling with modern best practices.
---

# Frontend Page & Component Building

## Instructions

1. **Page & Layout Structure**
   - Use semantic HTML (`header`, `main`, `section`, `footer`)
   - Responsive grid/flex layouts
   - Consistent spacing and alignment

2. **Component Design**
   - Reusable, modular components
   - Clear separation of structure, style, and behavior
   - Props/variants for flexibility

3. **Styling**
   - Mobile-first CSS
   - Use CSS Grid & Flexbox
   - Scalable design system (colors, spacing, typography)

4. **Responsiveness**
   - Breakpoints for mobile, tablet, desktop
   - Fluid typography and layouts
   - Touch-friendly interactions

## Best Practices
- Keep components small and reusable
- Follow consistent naming conventions
- Avoid inline styles
- Optimize for accessibility (ARIA, contrast, keyboard navigation)
- Test across screen sizes

## Example Structure
```html
<main class="page">
  <header class="page-header">
    <h1 class="title">Page Title</h1>
  </header>

  <section class="content-grid">
    <article class="card">
      <h2 class="card-title">Component Title</h2>
      <p class="card-text">Reusable component content.</p>
      <button class="btn-primary">Action</button>
    </article>
  </section>
</main>