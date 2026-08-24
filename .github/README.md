# 🌐 WebUp Industrial Engineering

> A modern, responsive HTML5 website showcasing industrial metal engineering, fabrication, and CNC machining projects with elegant design and accessibility features.

> **Note:** The metal/industrial engineering theme is used as a random example context. This template is versatile and can be easily adapted for any purpose — portfolios, small businesses, personal projects, non-profits, or any other use case by simply changing the content, images, and branding.

![Version](https://img.shields.io/badge/version-0.5.1-blue.svg)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![SEO Optimized](https://img.shields.io/badge/SEO-Optimized-green.svg)
![Accessibility](https://img.shields.io/badge/A11y-WCAG-blue.svg)
![Valid HTML5](https://img.shields.io/badge/HTML5-Valid-brightgreen.svg)
![Valid CSS3](https://img.shields.io/badge/CSS3-Valid-brightgreen.svg)

---

## ✨ Features

- 🎨 **Modern Design** - Clean HTML5 structure with semantic elements and ARIA labels
- 📱 **Fully Responsive** - Adaptive layout with tablet (≤768px) and mobile (≤480px) breakpoints
- 🧭 **Fixed Navigation Bar** - Button-style menu with dropdown for projects, stays visible while scrolling
- 🎯 **Active Page Indicator** - Current page highlighted in navigation menu
- 📱 **Mobile Optimized** - Scaled-down navigation, headings, content, and images for smaller screens
- 🖼️ **Interactive Gallery** - 5 metal engineering projects with paper shadow effects and rotation
- 🎨 **Button-Style Menu** - Modern navigation with hover effects, borders, and smooth transitions
- 📂 **Dropdown Menu** - Collapsible Projects menu with all 5 project detail pages
- ✅ **W3C Validated** - HTML5 and CSS3 pass official W3C validation with badge links in footer
- 🏗️ **Architecture Diagrams** - 7 PlantUML diagrams documenting structure, flow, and deployment
- 🔧 **Build Automation** - Makefile targets for diagrams, PDFs, and validation
- � **GitHub Actions** - Automated deployment to GitHub Pages and CI for documentation
- �📚 **Learning Resources** - Curated HTML5/CSS learning path with milestones and exercises
- 🔗 **Multi-Page Navigation** - Home, About, Contact, Impressum, and individual project detail pages
- ⚙️ **Custom Branding** - Compact 32px logo in navigation bar with favicon support
- 🎭 **Watermarked Backgrounds** - Beautiful project images as backgrounds on detail pages
- 🎨 **CSS Variable Theming** - Easy customization with centralized theme configuration
- 🌈 **5 Ready-Made Themes** - Blue, Gray, Green, Orange, and Navy color schemes included
- 🎨 **Dark Sepia Theme** - Warm, earthy color scheme for professional industrial look (default)
- ♿ **Accessibility** - ARIA labels, semantic HTML, keyboard navigation, and focus management
- 🔍 **SEO Optimized** - Meta descriptions, keywords, sitemap.xml, and proper heading structure
- 🔒 **Privacy Compliant** - About, Contact, and Impressum pages excluded from search engines
- 🤖 **Crawler Control** - robots.txt for search engine management
- 📚 **Comprehensive Documentation** - AsciiDoc guides for setup, theming, and deployment
- 👥 **humans.txt** - Credits and technology information
- 📋 **Professional Setup** - .gitignore, LICENSE, CHANGELOG, CONTRIBUTING files included

---

## 📂 Project Structure

```
webup/
├── 📄 .gitignore              # Git ignore patterns
├── 📄 LICENSE                 # MIT License
├── 📄 README.md               # This file
├── 📄 CHANGELOG.md            # Version history
├── 📄 CONTRIBUTING.md         # Contribution guidelines
├── 📄 Makefile                # Build automation (diagrams, PDFs, validation)
├── 📁 .github/                # GitHub Actions workflows
│   ├── 📄 README.md           # Workflows documentation
│   └── 📁 workflows/
│       ├── 📄 deploy.yml      # GitHub Pages deployment
│       └── 📄 build.yml       # Documentation build & validation
├── 📁 docs/                   # Documentation (AsciiDoc)
│   ├── 📄 README.adoc         # Documentation index
│   ├── 📄 index.adoc          # Main documentation
│   ├── 📄 theming.adoc        # CSS theming guide
│   ├── 📄 deployment.adoc     # Deployment instructions
│   ├── 📄 quick-reference.adoc # Quick reference card
│   ├── 📄 responsive-design.adoc # Responsive design guide
│   ├── 📄 learning.adoc       # HTML5/CSS learning guide
│   ├── 📄 diagrams.adoc       # Architecture diagrams gallery
│   ├── 📄 BUILD.adoc          # Build instructions
│   ├── 📕 index.pdf           # Main documentation (PDF)
│   ├── 📕 theming.pdf         # CSS theming guide (PDF)
│   ├── 📕 deployment.pdf      # Deployment guide (PDF)
│   ├── 📕 quick-reference.pdf # Quick reference (PDF)
│   ├── 📕 learning.pdf        # Learning guide (PDF)
│   ├── 📕 diagrams.pdf        # Diagrams gallery (PDF)
│   ├── 📕 BUILD.pdf           # Build instructions (PDF)
│   ├── 📁 diagrams/           # PlantUML source files
│   │   ├── project-structure.puml
│   │   ├── html-structure.puml
│   │   ├── css-architecture.puml
│   │   ├── navigation-flow.puml
│   │   ├── seo-architecture.puml
│   │   ├── theme-system.puml
│   │   └── deployment-workflow.puml
│   ├── 📁 images/             # Rendered diagram PNGs
│   │   ├── project-structure.png
│   │   ├── html-structure.png
│   │   ├── css-architecture.png
│   │   ├── navigation-flow.png
│   │   ├── seo-architecture.png
│   │   ├── theme-system.png
│   │   └── deployment-workflow.png
│   └── 📁 screenshots/        # Responsive layout screenshots
│       ├── desktop-layout.svg
│       ├── tablet-layout.svg
│       └── mobile-layout.svg
└── 📁 html/                   # Website root
    ├── 🏠 index.html          # Homepage with project gallery
    ├── 📖 about.html          # About page (excluded from search)
    ├── 📧 contact.html        # Contact page (excluded from search)
    ├── ⚖️ impressum.html      # Legal notice (excluded from search)
    ├── 🖼️ image1.html         # Project detail page 1
    ├── 🖼️ image2.html         # Project detail page 2
    ├── 🖼️ image3.html         # Project detail page 3
    ├── 🖼️ image4.html         # Project detail page 4
    ├── 🖼️ image5.html         # Project detail page 5
    ├── 🤖 robots.txt          # Web crawler control file
    ├── 🗺️ sitemap.xml         # SEO sitemap
    ├── 👥 humans.txt          # Credits and info
    ├── 📁 css/
    │   ├── 🎨 style.css       # Main stylesheet with CSS variables
    │   └── 📄 themes.md       # Theme variations guide
    └── 📁 images/
        ├── ⚙️ gear.ico        # Browser favicon
        ├── ⚙️ gear.png        # Site logo (32x32px in nav, 80x80px original)
        ├── ✅ validator-html5.svg  # HTML5 validation badge
        ├── ✅ validator-css.svg    # CSS validation badge
        ├── 🖼️ metal1.jpg      # Gallery image 1 (placeholder)
        ├── 🖼️ metal2.jpg      # Gallery image 2 (placeholder)
        ├── 🖼️ metal3.jpg      # Gallery image 3 (placeholder)
        ├── 🖼️ metal4.jpg      # Gallery image 4 (placeholder)
        └── 🖼️ metal5.jpg      # Gallery image 5 (placeholder)
```

---

## 🧭 Navigation Features

### Fixed Top Navigation Bar
- **Always Visible**: Navigation stays at the top while scrolling
- **Compact Logo**: 32px logo on the left side of the nav bar
- **Button-Style Menu Items**: Modern appearance with hover effects and borders
- **Active Page Highlighting**: Current page shown with background and border styling
- **Dropdown Menu**: "Projects" button reveals links to all 5 project detail pages
- **Keyboard Accessible**: Full keyboard navigation and focus management
- **Responsive**: Scales down on tablet (28px logo, smaller buttons) and mobile (24px logo, compact layout)

### Responsive Behavior
The navigation adapts to different screen sizes:
- **Desktop (>768px)**: Full-size nav with 32px logo, standard button padding
- **Tablet (≤768px)**: Reduced to 28px logo, smaller gaps, 40px top margin
- **Mobile (≤480px)**: Compact 24px logo, minimal spacing, 32px top margin

---

## 🚀 Getting Started

### ⚠️ Important: Image Licensing

**The current images in the `html/images/` folder are placeholders and must be replaced before commercial use.**

- Replace `metal1.jpg` through `metal5.jpg` with your own photos or properly licensed images
- The metal industry theme is just a random example — adapt the content for your actual project (portfolio, business, blog, showcase, etc.)
- Ensure you have the rights to use all images on your website
- Consider using:
  - Your own photography of projects/machinery
  - Licensed stock photos (Shutterstock, Adobe Stock, Getty Images)
  - Free stock photos with proper attribution (Unsplash, Pexels, Pixabay)
- Document image sources and keep license receipts
- Add attribution if required by the license

**Failure to use properly licensed images may result in copyright infringement issues.**

---

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/iosan/webup.git
   cd webup
   ```

2. **Open in browser**
   ```bash
   # Simply open the index.html file
   open html/index.html
   # or on Linux
   xdg-open html/index.html
   # or on Windows
   start html/index.html
   ```

3. **That's it!** No build process or dependencies required. 🎉

### Development

For local development with live reload, you can use any simple HTTP server:

```bash
# Python 3
cd html && python -m http.server 8000

# Node.js (with http-server installed)
cd html && npx http-server -p 8000

# PHP
cd html && php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

---

## � Responsive Design

The website is fully responsive with three optimized layout modes:

### Desktop (>768px)
- Full-size navigation with 32px logo
- Multi-column gallery with rotation effects
- 250px image boxes with generous spacing
- Complete visual experience

### Tablet (≤768px)
- Scaled navigation with 28px logo
- 2-column auto-fit gallery grid
- 180px image boxes with reduced spacing
- Optimized typography (0.95rem)

### Mobile (≤480px)
- Compact navigation with 24px logo
- Single-column centered gallery
- 140px image boxes, minimal spacing
- No rotation effects for cleaner look
- Right-aligned dropdown menu
- Stacked footer badges

**📸 See detailed layouts with screenshots**: `docs/responsive-design.adoc`

---

## �🔧 Build & Validation

### Build Documentation and Diagrams

The project includes a `Makefile` for automating diagram generation and PDF documentation:

```bash
# Regenerate all PlantUML diagrams to PNG
make diagrams

# Build all documentation PDFs
make pdfs

# Both diagrams and PDFs
make docs

# Validate HTML and CSS (requires network)
make validate-html
make validate-css
make validate-all
```

**Docker alternatives** (if you don't have PlantUML or asciidoctor-pdf installed locally):

```bash
make docker-diagrams
make docker-pdfs
```

See `docs/BUILD.adoc` for detailed build instructions and prerequisites.

### W3C Validation

Every page includes W3C validator badges in the footer. Click them to validate:
- **HTML5**: Uses Nu HTML Checker
- **CSS3**: Uses Jigsaw CSS Validator

Or validate locally:

```bash
make validate-all
```

---

## 🚀 GitHub Actions & Deployment

### Automated Workflows

The repository includes two GitHub Actions workflows in `.github/workflows/`:

#### 1. **deploy.yml** - GitHub Pages Deployment
Automatically deploys the `html/` directory to GitHub Pages when you push to `master` or `main`.

**Setup:**
1. Go to repository **Settings → Actions → General**
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Go to **Settings → Pages**
4. Set Source to **"Deploy from a branch"**
5. Select branch: **`gh-pages`** / folder: **`/ (root)`**
6. Push to `master`/`main` and your site deploys automatically!

Your site will be available at: `https://<username>.github.io/<repository>/`

#### 2. **build.yml** - Documentation Build (Optional)
Builds diagrams and PDFs on every push or pull request. Artifacts are available for download.

**What it does:**
- Installs PlantUML, Graphviz, and AsciiDoc tools
- Runs `make diagrams` to generate PNG diagrams
- Runs `make pdfs` to build documentation PDFs
- Uploads artifacts (PDFs and PNGs) for download

### Manual Deployment

For traditional hosting (FTP, shared hosting, VPS):

```bash
# Just upload the html/ directory contents
cd html
# Upload all files to your web server's public_html or www directory
```

See `docs/deployment.adoc` for detailed deployment guides including Netlify, Vercel, and custom domains.

---

## 🎨 Customization

### Change Colors with CSS Variables

The website now uses CSS variables for easy theming! Edit `html/css/style.css`:

```css
:root {
    /* Change these variables to customize your theme */
    --color-primary: #3d2f21;        /* Header/footer/nav background */
    --color-background: #f4f4f4;     /* Content background */
    --color-text-dark: #333;         /* Main text color */
    --spacing-md: 40px;              /* Adjust spacing */
    --image-size: 250px;             /* Gallery image size (180px tablet, 140px mobile) */
    
    /* Responsive breakpoints automatically adjust:
       - Navigation: 32px → 28px → 24px logo
       - Images: 250px → 180px → 140px boxes
       - Typography: Scaled down at 768px and 480px
    */
}
```

**5 Ready-Made Themes Available!**
See `html/css/themes.md` or `docs/theming.adoc` for:
- Blue Industrial Theme
- Modern Gray Theme
- Deep Green Theme
- Warm Orange Theme
- Professional Navy Theme

### Legacy Color Customization

You can also directly edit individual CSS rules:

```css
/* Header and Footer - Dark Sepia Theme */
header, footer {
    background-color: #3d2f21;  /* Change to your preferred color */
}

/* Content Background */
.content {
    background-color: #f4f4f4;  /* Light background - customize as needed */
}
```

### Replace Images

**⚠️ IMPORTANT: Replace placeholder images before publishing**

1. Add your own images or properly licensed images to `html/images/`
2. Use the same filenames (`metal1.jpg` through `metal5.jpg`) or update references
3. Update the image references in `html/index.html` if needed
4. Ensure image names match in the corresponding `imageX.html` pages
5. Recommended size: 250x250px or larger (maintains aspect ratio with `object-fit: cover`)
6. Keep documentation of image sources and licenses

**Image Sources:**
- Take your own photos (you own the copyright)
- Purchase from stock sites (Shutterstock, Adobe Stock, Getty Images)
- Use free stock photos (Unsplash, Pexels, Pixabay)
- Ensure proper licensing for commercial use

### Update Company Information

Edit the **Impressum page** (`html/impressum.html`) with your actual company details:
- Company name and address
- Contact information
- Legal representatives
- VAT ID and registration numbers

### Modify SEO

Update meta tags in each HTML file:
```html
<meta name="description" content="Your custom description">
<meta name="keywords" content="metal, steel, industrial, machinery, engineering, fabrication, cnc">
```

---

## 🎯 Key Features Explained

### 📸 Interactive Project Gallery
- 5 projects displayed with paper-like shadow effects
- Each image rotates slightly toward the center for visual interest
- Smooth hover effects with scale and rotation
- Click images to view detailed project pages with watermarked backgrounds

### 🎨 Professional Styling
- **Header**: Dark sepia background with fixed gear logo
- **Content**: Flexible layout with clean typography
- **Footer**: Fixed at bottom of viewport with impressum link
- **Navigation**: Responsive menu with hover effects and ARIA labels

### ♿ Accessibility Features
- Semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`)
- ARIA labels for navigation and links
- `aria-current="page"` for current page indication
- Descriptive alt text for all images
- Keyboard navigation support

### 🔍 SEO Optimization
- Unique meta descriptions for each page
- Targeted keywords (metal, steel, industrial, machinery, engineering, fabrication, cnc)
- Proper heading hierarchy (H1, H2, H3)
- Author meta tags
- Structured content with semantic elements

### 🔒 Privacy & Legal Compliance
- Impressum page with complete legal notice template
- About and Contact pages excluded from search engines for privacy
- Excluded from search engines via:
  - Meta robots tags (`noindex, nofollow, noarchive, nosnippet`)
  - robots.txt configuration
- Accessible via footer link (Impressum) and navigation (About, Contact) on all pages

### 🔗 Navigation Structure
```
Home (index.html)
├── About (about.html) [excluded from search]
├── Contact (contact.html) [excluded from search]
├── Impressum (impressum.html) [excluded from search]
├── Project 1 Detail (image1.html) [with watermark]
├── Project 2 Detail (image2.html) [with watermark]
├── Project 3 Detail (image3.html) [with watermark]
├── Project 4 Detail (image4.html) [with watermark]
└── Project 5 Detail (image5.html) [with watermark]
```

---

## 📋 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Opera (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 🛠️ Technical Details

### CSS Organization
The stylesheet is organized into clear sections with CSS variables:
- **CSS Variables** - Centralized theme configuration
- **Global Styles** - Base resets and typography
- **Header Styles** - Navigation and branding area
- **Logo Styles** - Brand logo positioning
- **Navigation Styles** - Menu and links
- **Content Area Styles** - Main content layout
- **Watermark Background Styles** - Background overlays
- **Image Gallery Styles** - Project gallery effects
- **Footer Styles** - Bottom section

All colors, spacing, and sizes use CSS variables for easy customization!

### HTML5 Best Practices
- Valid DOCTYPE declaration
- Proper meta tags for character encoding and viewport
- Semantic HTML elements
- ARIA accessibility attributes
- Organized head section with comments
- Clean code structure with proper indentation

---

## � Version History

### v0.5.1 (Current - November 13, 2025)
- Added GitHub Actions workflows for automated deployment
- Fixed build and deployment issues
- Equal gallery spacing (top and bottom margins)

### v0.5.0 (November 6, 2025)

**Major Release - Responsive Design & Navigation Improvements**
- ✨ Initial release
- 🎨 Dark sepia theme with warm industrial aesthetics
- 🌈 CSS variables system with 5 ready-made alternative themes
- 🖼️ 5-project gallery with paper shadows and rotation effects
- ✅ W3C validated HTML5 and CSS3 with interactive validator badges in footer
- 🏗️ Architecture documentation with 7 PlantUML diagrams (project structure, HTML, CSS, navigation, SEO, theming, deployment)
- � Diagrams gallery (diagrams.adoc) with thumbnail index and full-size views
- 🔧 Build automation via Makefile (diagrams, PDFs, validation)
- 📚 Learning guide (learning.adoc) with curated HTML5/CSS resources and milestones
- �📱 Responsive design for all devices
- ⚙️ Custom gear logo and favicon
- ♿ Full accessibility features with ARIA labels and semantic HTML (`<figure>`, `<figcaption>`)
- 🔍 SEO optimized with meta tags, keywords, and sitemap.xml
- 🔒 Privacy-compliant pages (About, Contact, Impressum excluded from search)
- 🤖 robots.txt for crawler management
- 👥 humans.txt for credits and technology info
- 🎭 Watermarked backgrounds on project detail pages
- 📚 Comprehensive AsciiDoc documentation (setup, theming, deployment, learning, build, diagrams)
- 📋 Professional project setup (.gitignore, LICENSE, CHANGELOG, CONTRIBUTING)
- ⚠️ **Note**: Placeholder images must be replaced with properly licensed images before commercial use

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

**⚠️ Image Licensing Notice:** The placeholder images (metal1-5.jpg, gear.png, gear.ico) are NOT covered by the MIT License and must be replaced with properly licensed images before commercial use.

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder (AsciiDoc and PDF formats):

**AsciiDoc Format:**
- **[Main Documentation](docs/index.adoc)** - Complete project guide
- **[Theming Guide](docs/theming.adoc)** - CSS customization and themes
- **[Deployment Guide](docs/deployment.adoc)** - Hosting and deployment instructions
- **[Quick Reference Card](docs/quick-reference.adoc)** - Fast lookup guide for common tasks
- **[Learning Guide](docs/learning.adoc)** - HTML5/CSS learning path with resources and milestones
- **[Architecture Diagrams](docs/diagrams.adoc)** - All 7 architecture diagrams in one gallery
- **[Build Instructions](docs/BUILD.adoc)** - How to regenerate diagrams and PDFs

**PDF Format:**
- **[Main Documentation (PDF)](docs/index.pdf)** - Complete project guide
- **[Theming Guide (PDF)](docs/theming.pdf)** - CSS customization and themes
- **[Deployment Guide (PDF)](docs/deployment.pdf)** - Hosting and deployment instructions
- **[Quick Reference Card (PDF)](docs/quick-reference.pdf)** - Fast lookup guide
- **[Learning Guide (PDF)](docs/learning.pdf)** - HTML5/CSS learning resources
- **[Architecture Diagrams (PDF)](docs/diagrams.pdf)** - All diagrams printable
- **[Build Instructions (PDF)](docs/BUILD.pdf)** - Build automation guide

View AsciiDoc files using:
- VS Code with AsciiDoc extension
- Command line: `asciidoctor docs/index.adoc`
- GitHub (automatically renders .adoc files)

---

## 👤 Author

**iosan**

- GitHub: [@iosan](https://github.com/iosan)
- Repository: [webup](https://github.com/iosan/webup)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](https://github.com/iosan/webup/issues) if you want to contribute.

### Development Guidelines
1. Maintain semantic HTML structure
2. Keep accessibility features intact
3. Follow the existing code organization
4. Test across multiple browsers
5. Update documentation as needed

---

## 🙏 Acknowledgments

- Design inspired by modern industrial aesthetics
- Paper shadow effects for engaging visual presentation
- Focus on accessibility and web standards compliance

---

<div align="center">
  <p>Made with ❤️ and ⚙️ by iosan</p>
  <p>⭐️ Star this repo if you like it!</p>
  <p><strong>WebUp Industrial Engineering</strong> - Precision. Quality. Innovation.</p>
</div>

