/**
 * AI Construction Assistant - Translation System
 * Developer: Andel Albdesk
 * Copyright (c) 2026 Andel Albdesk. All rights reserved.
 */

const translations = {
    en: {
        // Header & Navigation
        appTitle: "🏗️ AI Construction Assistant",
        dashboard: "Dashboard",
        logout: "Logout",
        login: "Login",
        register: "Register",

        // Login Page
        loginHeader: "Login",
        username: "Username",
        password: "Password",
        confirmPassword: "Confirm Password",
        email: "Email",
        loginButton: "Login",
        registerButton: "Register",
        noAccount: "Don't have an account?",
        registerHere: "Register here",
        haveAccount: "Already have an account?",
        loginHere: "Login here",

        // Dashboard
        myProjects: "My Projects",
        createNewProject: "Create New Project",
        createProject: "Create Project",
        projectName: "Project Name",
        projectNamePlaceholder: "e.g., Tirana Construction Project",
        description: "Description",
        descriptionOptional: "Description (Optional)",
        descriptionPlaceholder: "Brief description of the project...",
        cancel: "Cancel",

        // Project Cards
        contracts: "Contracts",
        laws: "Laws",
        queries: "Queries",
        uploadContract: "Upload Contract",
        uploadLaw: "Upload Law",
        askQuestions: "Ask Questions",
        viewDetails: "View Details",
        deleteProject: "Delete",
        confirmDelete: "Are you sure you want to delete this project?",

        // Upload Contract Page
        uploadContractTitle: "Upload Construction Contract",
        selectFiles: "Select Files",
        dragDrop: "or drag and drop files here",
        supportedFormats: "Supported formats: PDF, Word (DOCX/DOC), Apple Pages",
        maxFileSize: "Maximum file size: 50MB",
        contractType: "Contract Type",
        contractTypePlaceholder: "e.g., Concrete Delivery Agreement",
        parties: "Parties Involved",
        partiesPlaceholder: "e.g., Company A, Company B",
        uploadButton: "Upload & Process",
        processing: "Processing...",
        uploadedContracts: "Uploaded Contracts",
        fileName: "File Name",
        pages: "Pages",
        uploadedAt: "Uploaded",
        status: "Status",
        pending: "Pending",
        completed: "Completed",
        failed: "Failed",

        // Upload Law Page
        uploadLawTitle: "Upload Albanian Construction Law",
        lawNumber: "Law Number",
        lawNumberPlaceholder: "e.g., 32/5",
        lawTitle: "Law Title",
        lawTitlePlaceholder: "e.g., Albanian Construction Safety Law",
        year: "Year",
        yearPlaceholder: "e.g., 2023",
        uploadedLaws: "Uploaded Laws",

        // Query Page
        askQuestionsTitle: "Ask Questions About Contracts & Laws",
        conversation: "Conversation",
        startNewConversation: "Start New Conversation",
        newChat: "New Chat",
        askPlaceholder: "Ask",
        askQuestion: "Ask Question",
        you: "You",
        aiAssistant: "AI Assistant",
        copyAnswer: "📋 Copy Answer",
        copied: "✅ Copied!",
        citationsFromContracts: "Citations from Contracts",
        citationsFromLaws: "Citations from Laws",
        document: "Document",
        page: "Page",
        clause: "Clause",
        article: "Article",
        relevanceScore: "Relevance",
        showText: "📖 Show Text",
        hideText: "📖 Hide Text",
        copyText: "📋 Copy",
        sourceTextNotAvailable: "Source text not available for this citation. Only new questions after the latest update include source text.",
        noCitations: "No citations",
        loading: "Loading...",
        yourConversations: "Your Conversations",
        conversationDescription: "Click on any conversation below to view and review all questions and answers.",
        loadingHistory: "Loading history...",
        disclaimer: "Disclaimer:",
        disclaimerText: "This tool interprets text from uploaded documents only. It is not a substitute for professional legal advice. Always consult with a qualified construction lawyer for critical decisions.",
        loadingProject: "Loading project...",

        // Footer
        footerTitle: "AI Construction Contract & Law Assistant",
        developedBy: "Developed by",
        copyright: "© 2026 Andel Albdesk. All rights reserved.",

        // Messages & Alerts
        success: "Success!",
        error: "Error",
        warning: "Warning",
        info: "Information",

        // Common Actions
        save: "Save",
        delete: "Delete",
        edit: "Edit",
        view: "View",
        close: "Close",
        back: "← Back to Dashboard",
        next: "Next",
        submit: "Submit",
        confirm: "Confirm",
        search: "Search",

        // Query Page - Dynamic Content
        noMessagesYet: "No messages in this conversation yet.",
        startNewConversationPrompt: "Start a new conversation by asking a question below.",
        noConversationsYet: "No conversations yet. Start by asking a question above!",
        sources: "📚 Sources:",
        contractsLabel: "📄 Contracts:",
        lawsLabel: "⚖️ Laws:",
        relevant: "relevant",
        messages: "messages",
        message: "message",
        active: "Active",
        copiedSuccess: "✅ Copied!"
    },

    sq: {
        // Header & Navigation
        appTitle: "🏗️ Asistenti AI për Ndërtim",
        dashboard: "Paneli",
        logout: "Dil",
        login: "Hyr",
        register: "Regjistrohu",

        // Login Page
        loginHeader: "Hyrje",
        username: "Emri i përdoruesit",
        password: "Fjalëkalimi",
        confirmPassword: "Konfirmo Fjalëkalimin",
        email: "Email",
        loginButton: "Hyr",
        registerButton: "Regjistrohu",
        noAccount: "Nuk keni llogari?",
        registerHere: "Regjistrohuni këtu",
        haveAccount: "Keni tashmë llogari?",
        loginHere: "Hyni këtu",

        // Dashboard
        myProjects: "Projektet e Mia",
        createNewProject: "Krijo Projekt të Ri",
        createProject: "Krijo Projekt",
        projectName: "Emri i Projektit",
        projectNamePlaceholder: "p.sh., Projekti i Ndërtimit në Tiranë",
        description: "Përshkrimi",
        descriptionOptional: "Përshkrimi (Opsionale)",
        descriptionPlaceholder: "Përshkrim i shkurtër i projektit...",
        cancel: "Anulo",

        // Project Cards
        contracts: "Kontrata",
        laws: "Ligje",
        queries: "Pyetje",
        uploadContract: "Ngarko Kontratë",
        uploadLaw: "Ngarko Ligj",
        askQuestions: "Bëj Pyetje",
        viewDetails: "Shiko Detajet",
        deleteProject: "Fshi",
        confirmDelete: "Jeni i sigurt që dëshironi të fshini këtë projekt?",

        // Upload Contract Page
        uploadContractTitle: "Ngarko Kontratë Ndërtimi",
        selectFiles: "Zgjidh Skedarë",
        dragDrop: "ose zvarrit dhe lësho skedarët këtu",
        supportedFormats: "Formate të mbështetura: PDF, Word (DOCX/DOC), Apple Pages",
        maxFileSize: "Madhësia maksimale e skedarit: 50MB",
        contractType: "Lloji i Kontratës",
        contractTypePlaceholder: "p.sh., Marrëveshje për Furnizim Betoni",
        parties: "Palët e Përfshira",
        partiesPlaceholder: "p.sh., Kompania A, Kompania B",
        uploadButton: "Ngarko & Përpuno",
        processing: "Duke përpunuar...",
        uploadedContracts: "Kontratat e Ngarkuara",
        fileName: "Emri i Skedarit",
        pages: "Faqe",
        uploadedAt: "Ngarkuar",
        status: "Statusi",
        pending: "Në pritje",
        completed: "Përfunduar",
        failed: "Dështuar",

        // Upload Law Page
        uploadLawTitle: "Ngarko Ligj Ndërtimi Shqiptar",
        lawNumber: "Numri i Ligjit",
        lawNumberPlaceholder: "p.sh., 32/5",
        lawTitle: "Titulli i Ligjit",
        lawTitlePlaceholder: "p.sh., Ligji për Sigurinë në Ndërtim",
        year: "Viti",
        yearPlaceholder: "p.sh., 2023",
        uploadedLaws: "Ligjet e Ngarkuara",

        // Query Page
        askQuestionsTitle: "Bëj Pyetje Rreth Kontratave & Ligjeve",
        conversation: "Bisedë",
        startNewConversation: "Fillo Bisedë të Re",
        newChat: "Bisedë e Re",
        askPlaceholder: "Pyet",
        askQuestion: "Bëj Pyetje",
        you: "Ju",
        aiAssistant: "Asistenti AI",
        copyAnswer: "📋 Kopjo Përgjigjen",
        copied: "✅ U kopjua!",
        citationsFromContracts: "Citate nga Kontratat",
        citationsFromLaws: "Citate nga Ligjet",
        document: "Dokumenti",
        page: "Faqja",
        clause: "Neni",
        article: "Artikulli",
        relevanceScore: "Rëndësia",
        showText: "📖 Shfaq Tekstin",
        hideText: "📖 Fsheh Tekstin",
        copyText: "📋 Kopjo",
        sourceTextNotAvailable: "Teksti burimor nuk është i disponueshëm për këtë citim. Vetëm pyetjet e reja pas përditësimit të fundit përfshijnë tekstin burimor.",
        noCitations: "Nuk ka citate",
        loading: "Duke ngarkuar...",
        yourConversations: "Bisedat Tuaja",
        conversationDescription: "Klikoni në çdo bisedë më poshtë për të parë dhe rishikuar të gjitha pyetjet dhe përgjigjet.",
        loadingHistory: "Duke ngarkuar historikun...",
        disclaimer: "Kujdes:",
        disclaimerText: "Ky mjet interpreton tekstin vetëm nga dokumentet e ngarkuara. Nuk është zëvendësues i këshillës ligjore profesionale. Gjithmonë konsultohuni me një avokat ndërtimi të kualifikuar për vendime kritike.",
        loadingProject: "Duke ngarkuar projektin...",

        // Footer
        footerTitle: "Asistenti AI për Kontrata & Ligje Ndërtimi",
        developedBy: "Zhvilluar nga",
        copyright: "© 2026 Andel Albdesk. Të gjitha të drejtat e rezervuara.",

        // Messages & Alerts
        success: "Sukses!",
        error: "Gabim",
        warning: "Paralajmërim",
        info: "Informacion",

        // Common Actions
        save: "Ruaj",
        delete: "Fshi",
        edit: "Ndrysho",
        view: "Shiko",
        close: "Mbyll",
        back: "← Kthehu te Paneli",
        next: "Vazhdo",
        submit: "Dërgo",
        confirm: "Konfirmo",
        search: "Kërko",

        // Query Page - Dynamic Content
        noMessagesYet: "Ende nuk ka mesazhe në këtë bisedë.",
        startNewConversationPrompt: "Fillo një bisedë të re duke bërë një pyetje më poshtë.",
        noConversationsYet: "Ende nuk ka biseda. Fillo duke bërë një pyetje më sipër!",
        sources: "📚 Burimet:",
        contractsLabel: "📄 Kontratat:",
        lawsLabel: "⚖️ Ligjet:",
        relevant: "përkatëse",
        messages: "mesazhe",
        message: "mesazh",
        active: "Aktive",
        copiedSuccess: "✅ U kopjua!"
    }
};

// Language Manager
class LanguageManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('language') || 'en';
        this.init();
    }

    init() {
        // Set initial language
        this.setLanguage(this.currentLanguage, false);

        // Add language switcher to all pages if it doesn't exist
        this.addLanguageSwitcher();
    }

    setLanguage(lang, reload = true) {
        if (!translations[lang]) {
            console.error(`Language ${lang} not found`);
            return;
        }

        this.currentLanguage = lang;
        localStorage.setItem('language', lang);

        // Update all translatable elements
        this.updatePageTranslations();

        // Update language buttons
        this.updateLanguageButtons();

        if (reload) {
            // Trigger custom event for dynamic content
            window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
        }
    }

    translate(key) {
        return translations[this.currentLanguage][key] || key;
    }

    updatePageTranslations() {
        // Update all elements with data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.translate(key);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.placeholder !== undefined) {
                    element.placeholder = translation;
                }
            } else {
                element.textContent = translation;
            }
        });

        // Update placeholders separately
        document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
            const key = element.getAttribute('data-translate-placeholder');
            element.placeholder = this.translate(key);
        });

        // Update title attributes
        document.querySelectorAll('[data-translate-title]').forEach(element => {
            const key = element.getAttribute('data-translate-title');
            element.title = this.translate(key);
        });
    }

    updateLanguageButtons() {
        const enBtn = document.getElementById('lang-en');
        const sqBtn = document.getElementById('lang-sq');

        if (enBtn && sqBtn) {
            enBtn.classList.toggle('active', this.currentLanguage === 'en');
            sqBtn.classList.toggle('active', this.currentLanguage === 'sq');
        }
    }

    addLanguageSwitcher() {
        // Check if language switcher already exists
        if (document.querySelector('.language-switcher')) {
            return;
        }

        // Find header nav-links
        const navLinks = document.querySelector('.nav-links');
        if (!navLinks) {
            return;
        }

        // Create language switcher
        const langSwitcher = document.createElement('div');
        langSwitcher.className = 'language-switcher';
        langSwitcher.style.display = 'flex';
        langSwitcher.style.gap = '8px';
        langSwitcher.style.marginLeft = '12px';

        langSwitcher.innerHTML = `
            <button id="lang-en" class="lang-btn ${this.currentLanguage === 'en' ? 'active' : ''}"
                    onclick="languageManager.setLanguage('en')">
                English
            </button>
            <button id="lang-sq" class="lang-btn ${this.currentLanguage === 'sq' ? 'active' : ''}"
                    onclick="languageManager.setLanguage('sq')">
                Shqip
            </button>
        `;

        navLinks.appendChild(langSwitcher);
    }
}

// Initialize language manager
const languageManager = new LanguageManager();

// Make it globally available
window.languageManager = languageManager;
window.translations = translations;
