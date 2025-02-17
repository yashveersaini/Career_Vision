document.addEventListener('DOMContentLoaded', function() {
    loadJobs();
    setupFilters();
});

let jobsData = [];

async function loadJobs() {
    try {
        const response = await fetch('/get_jobs');
        jobsData = await response.json();
        displayJobs(jobsData);
        populateFilters(jobsData);
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobListings').innerHTML = 
            '<div class="alert alert-danger">Error loading job listings. Please try again later.</div>';
    }
}

function displayJobs(jobs) {
    const jobListings = document.getElementById('jobListings');
    jobListings.innerHTML = '';

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        
        const skills = job.skills.split(',').map(skill => skill.trim());
        const skillsHtml = skills.map(skill => 
            `<span class="skill-tag">${skill}</span>`
        ).join('');

        jobCard.innerHTML = `
            <h3 class="job-title">${job.job_role}</h3>
            <div class="job-category">${job.interest}</div>
            <div class="job-skills">${skillsHtml}</div>
        `;
        
        jobListings.appendChild(jobCard);
    });
}

function populateFilters(jobs) {
    const interestFilter = document.getElementById('interestFilter');
    const interests = [...new Set(jobs.map(job => job.interest))];
    
    interests.forEach(interest => {
        const option = document.createElement('option');
        option.value = interest;
        option.textContent = interest;
        interestFilter.appendChild(option);
    });
}

function setupFilters() {
    const searchInput = document.getElementById('searchInput');
    const interestFilter = document.getElementById('interestFilter');

    searchInput.addEventListener('input', filterJobs);
    interestFilter.addEventListener('change', filterJobs);
}

function filterJobs() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedInterest = document.getElementById('interestFilter').value;

    const filteredJobs = jobsData.filter(job => {
        const matchesSearch = job.job_role.toLowerCase().includes(searchTerm) ||
                            job.skills.toLowerCase().includes(searchTerm);
        const matchesInterest = !selectedInterest || job.interest === selectedInterest;
        return matchesSearch && matchesInterest;
    });

    displayJobs(filteredJobs);
}
