<script>    import { onMount } from 'svelte';
    import { getMedicalData } from '$lib/firebase';
    import MedicalForm from './medicalform.svelte';
    import { showDailyReminderNotification } from '$lib/services/notification-service';
    
    export let userId;
    
    let loading = true;
    let error = null;
    let medicalData = null;
    let isEditing = false;
    
    // Constants for unit conversion
    const ML_PER_CUP = 237; // 1 cup = 237 ml (approximately)
    
    // Categories for displaying grouped medical conditions
    const medicalConditionCategories = [
        { 
            name: 'Cardiovascular', 
            conditions: [
                { id: 'cardiovascular_disease', label: 'Cardiovascular Disease' },
                { id: 'high_blood_pressure', label: 'High Blood Pressure' }
            ]
        },
        { 
            name: 'Metabolic', 
            conditions: [
                { id: 'diabetes', label: 'Diabetes' },
                { id: 'thyroid_disorder', label: 'Thyroid Disorder' }
            ]
        },
        { 
            name: 'Respiratory', 
            conditions: [
                { id: 'respiratory_issues', label: 'Respiratory Issues' },
                { id: 'asthma', label: 'Asthma' }
            ]
        },
        { 
            name: 'Other Conditions', 
            conditions: [
                { id: 'heat_sensitivity', label: 'Heat Sensitivity' },
                { id: 'kidney_disease', label: 'Kidney Disease' },
                { id: 'neurological_disorders', label: 'Neurological Disorders' }
            ]
        }
    ];
    
    // Drink types for fluid intake
    const drinkTypes = [
        { id: 'water_amount', label: 'Water' },
        { id: 'electrolyte_drinks_amount', label: 'Electrolyte Drinks' },
        { id: 'coconut_water_amount', label: 'Coconut Water' },
        { id: 'fruit_juice_amount', label: 'Fruit Juice' },
        { id: 'iced_tea_amount', label: 'Iced Tea' },
        { id: 'soda_amount', label: 'Soda' },
        { id: 'milk_tea_amount', label: 'Milk Tea' },
        { id: 'coffee_amount', label: 'Coffee' },
        { id: 'herbal_tea_amount', label: 'Herbal Tea' }
    ];
    
    onMount(async () => {
        await loadMedicalData();
    });
    
    async function loadMedicalData() {
        loading = true;
        
        try {
            const { data, error: fetchError } = await getMedicalData(userId);
            
            if (data) {
                medicalData = data;
            } else {
                error = fetchError;
            }
        } catch (err) {
            console.error("Error loading medical data:", err);
            error = "Unable to load medical data. Please try again.";
        } finally {
            loading = false;
        }
    }
    
    function toggleEdit() {
        isEditing = !isEditing;
    }
    
    function handleFormCompleted() {
        isEditing = false;
        loadMedicalData();
    }
    
    function handleFormCancel() {
        isEditing = false;
    }
    
    // Helper functions for formatting display values
    
    // Format activity level for display
    function formatActivityLevel(level) {
        switch(level) {
            case 'sedentary': return 'Sedentary';
            case 'light': return 'Light Activity';
            case 'moderate': return 'Moderate Activity';
            case 'vigorous': return 'Vigorous Activity';
            case 'extreme': return 'Extreme Activity';
            default: return 'Not specified';
        }
    }
    
    // Format activity duration for display
    function formatActivityDuration(duration) {
        switch(duration) {
            case 'less_than_30_mins': return 'Less than 30 minutes';
            case '30_to_60_mins': return '30-60 minutes';
            case '1_to_2_hours': return '1-2 hours';
            case 'more_than_2_hours': return 'More than 2 hours';
            default: return 'Not specified';
        }
    }
    
    // Format gender for display
    function formatGender(gender) {
        switch(gender) {
            case 'male': return 'Male';
            case 'female': return 'Female';
            case 'non-binary': return 'Non-binary';
            case 'prefer-not-to-say': return 'Prefer not to say';
            default: return 'Not specified';
        }
    }
    
    // Get the total daily fluid intake in ml
    function getTotalFluidIntake() {
        if (!medicalData?.fluid_intake) return 0;
        
        let total = 0;
        for (const drinkType of drinkTypes) {
            const amount = medicalData.fluid_intake[drinkType.id] || 0;
            total += amount;
        }
        
        // Add other fluid if any
        if (medicalData.fluid_intake.other_fluid_amount) {
            total += medicalData.fluid_intake.other_fluid_amount;
        }
        
        return total;
    }
    
    // Convert ml to cups for display
    function mlToCups(ml) {
        return Math.round((ml / ML_PER_CUP) * 10) / 10;
    }
    
    // Format fluid amount with both ml and cups
    function formatFluidAmount(ml) {
        if (!ml || ml === 0) return '0 ml (0 cups)';
        const cups = mlToCups(ml);
        return `${ml} ml (${cups} ${cups === 1 ? 'cup' : 'cups'})`;
    }
    
    // Calculate if user drinks enough water per day (simple estimate)
    function getHydrationStatus() {
        if (!medicalData?.biometrics?.weight || !medicalData?.fluid_intake) return null;
        
        // Simple estimate: Person should drink ~30ml per kg of body weight
        const recommendedTotal = medicalData.biometrics.weight * 30;
        const waterAmount = medicalData.fluid_intake.water_amount || 0;
        const totalFluid = getTotalFluidIntake();
        
        if (waterAmount < recommendedTotal * 0.5) {
            return {
                status: 'concern',
                message: 'You may not be drinking enough water. Consider increasing your daily water intake.'
            };
        } else if (totalFluid < recommendedTotal) {
            return {
                status: 'warning',
                message: 'Your total fluid intake is below the recommended amount. Try to drink more fluids throughout the day.'
            };
        } else {
            return {
                status: 'good',
                message: 'Your hydration level appears adequate based on your weight.'
            };
        }
    }
    
    // Get a list of active medical conditions
    function getActiveMedicalConditions() {
        if (!medicalData?.medical_conditions) return [];
        
        const activeConditions = [];
        
        // Collect from all categories
        for (const category of medicalConditionCategories) {
            for (const condition of category.conditions) {
                if (medicalData.medical_conditions[condition.id]) {
                    activeConditions.push(condition.label);
                }
            }
        }
        
        // Add other conditions if specified
        if (medicalData.medical_conditions.other && 
            medicalData.medical_conditions.other.has_other && 
            medicalData.medical_conditions.other.description) {
            activeConditions.push(medicalData.medical_conditions.other.description);
        }
        
        return activeConditions;
    }
    
    // Get a list of active medications
    function getActiveMedications() {
        if (!medicalData?.medications) return [];
        
        const activeMeds = [];
        
        if (medicalData.medications.diuretics) activeMeds.push('Diuretics');
        if (medicalData.medications.blood_pressure_medications) activeMeds.push('Blood Pressure Medications');
        if (medicalData.medications.antihistamines) activeMeds.push('Antihistamines');
        if (medicalData.medications.antidepressants) activeMeds.push('Antidepressants');
        if (medicalData.medications.antipsychotics) activeMeds.push('Antipsychotics');
        
        // Add other medications if specified
        if (medicalData.medications.other && 
            medicalData.medications.other.has_other && 
            medicalData.medications.other.description) {
            activeMeds.push(medicalData.medications.other.description);
        }
        
        return activeMeds;
    }
    
    // Get an array of active heat conditions
    function getActiveHeatConditions() {
        if (!medicalData?.heat_conditions) return [];
        
        const conditions = [];
        
        if (medicalData.heat_conditions.mild_dehydration) conditions.push('Mild Dehydration');
        if (medicalData.heat_conditions.heat_rash) conditions.push('Heat Rash');
        if (medicalData.heat_conditions.heat_stroke) conditions.push('Heat Stroke');
        if (medicalData.heat_conditions.muscle_fatigue) conditions.push('Muscle Fatigue');
        if (medicalData.heat_conditions.heat_syncope) conditions.push('Heat Syncope (Fainting)');
        if (medicalData.heat_conditions.heat_edema) conditions.push('Heat Edema (Swelling)');
        if (medicalData.heat_conditions.heat_exhaustion) conditions.push('Heat Exhaustion');
        
        return conditions;
    }    // Calculate hydration status based on profile data
    $: hydrationStatus = medicalData ? getHydrationStatus() : null;
    $: totalFluidIntake = medicalData ? getTotalFluidIntake() : 0;
    $: medicalConditions = medicalData ? getActiveMedicalConditions() : [];
    $: medications = medicalData ? getActiveMedications() : [];
    $: heatConditions = medicalData ? getActiveHeatConditions() : [];
    
    // Generate notifications for health alerts when data changes and thresholds are met
    $: if (medicalData && !loading) {
        // Check hydration status for alerts
        if (hydrationStatus && (hydrationStatus.status === 'concern' || hydrationStatus.status === 'warning')) {
            showDailyReminderNotification(
                'hydration-reminder',
                hydrationStatus.message,
                'Hydration Reminder',
                'warning'
            );
        }
        
        // Check heat conditions for alerts
        if (heatConditions.length > 1) {
            showDailyReminderNotification(
                'heat-sensitivity-reminder',
                'You have reported multiple heat-related conditions that may increase your risk in hot environments. Take extra precautions on hot days.',
                'Heat Sensitivity Reminder',
                'warning'
            );
        }
    }
</script>

<div class="medical-profile">
    {#if loading}
        <div class="loading">
            <span class="spinner"></span>
            <p>Loading medical profile...</p>
        </div>
    {:else if error}
        <div class="error">
            <p>{error}</p>
            <button on:click={loadMedicalData} class="retry-btn">Try Again</button>
        </div>    {:else if isEditing}
        <MedicalForm 
            {userId} 
            initialData={medicalData} 
            isEditing={true}
            on:completed={handleFormCompleted}
            on:cancel={handleFormCancel}
        />{:else if medicalData}
          <div class="medical-data"><!-- Demographics & Biometrics Section -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Demographics & Biometrics</h3>
                    {#if medicalData.demographics?.age && medicalData.biometrics?.height && medicalData.biometrics?.weight}
                        <div class="bmi-indicator">
                            {#if medicalData.biometrics?.weight && medicalData.biometrics?.height}
                                {@const bmi = Math.round((medicalData.biometrics.weight / Math.pow(medicalData.biometrics.height / 100, 2)) * 10) / 10}
                                <span class="bmi-value">BMI: {bmi}</span>
                                <span class="bmi-category 
                                    {bmi < 18.5 ? 'underweight' : 
                                     bmi < 25 ? 'normal' : 
                                     bmi < 30 ? 'overweight' : 'obese'}">
                                    {bmi < 18.5 ? 'Underweight' : 
                                     bmi < 25 ? 'Normal' : 
                                     bmi < 30 ? 'Overweight' : 'Obese'}
                                </span>
                            {/if}
                        </div>
                    {/if}
                </div>
                <div class="section-body demographics-biometrics">
                    <div class="biometrics-stats">
                        <div class="stat-row">
                            <span class="stat-label">Age</span>
                            <span class="stat-value">{medicalData.demographics?.age || '—'}</span>
                            <span class="stat-unit">years</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Gender</span>
                            <span class="stat-value">
                                {#if medicalData.demographics?.gender === 'male'}Male
                                {:else if medicalData.demographics?.gender === 'female'}Female
                                {:else}Other{/if}
                            </span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Height</span>
                            <span class="stat-value">{medicalData.biometrics?.height || '—'}</span>
                            <span class="stat-unit">cm</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Weight</span>
                            <span class="stat-value">{medicalData.biometrics?.weight || '—'}</span>
                            <span class="stat-unit">kg</span>
                        </div>
                    </div>
                </div>
            </div><!-- Medical Conditions Section -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Medical Conditions</h3>
                    <div class="conditions-indicator">
                        <span class="conditions-count">{medicalConditions.length}</span>
                        <span class="conditions-status">{medicalConditions.length ? 'Active' : 'None'}</span>
                    </div>
                </div>
                <div class="section-body">
                    {#if medicalConditions.length === 0}
                        <div class="empty-state">
                            <div class="empty-icon">🩺</div>
                            <p>No medical conditions reported</p>
                        </div>
                    {:else}
                        <div class="conditions-container">
                            {#each medicalConditionCategories as category}
                                {@const categoryConditions = category.conditions.filter(c => medicalData.medical_conditions[c.id])}
                                {#if categoryConditions.length > 0}
                                    <div class="condition-category">
                                        <div class="category-header">
                                            <span class="category-name">{category.name}</span>
                                            <span class="category-count">{categoryConditions.length}</span>
                                        </div>
                                        <div class="condition-cards">
                                            {#each categoryConditions as condition}
                                                <div class="condition-card">
                                                    <div class="condition-icon-container">
                                                        <span class="condition-icon">
                                                            {#if category.name === 'Cardiovascular'}❤️
                                                            {:else if category.name === 'Metabolic'}⚡
                                                            {:else if category.name === 'Respiratory'}🫁
                                                            {:else}⚠️
                                                            {/if}
                                                        </span>
                                                    </div>
                                                    <span class="condition-name">{condition.label}</span>
                                                </div>
                                            {/each}
                                        </div>
                                    </div>
                                {/if}
                            {/each}
                            
                            {#if medicalData.medical_conditions?.other?.has_other && medicalData.medical_conditions?.other?.description}
                                <div class="condition-category">
                                    <div class="category-header">
                                        <span class="category-name">Other</span>
                                        <span class="category-count">1</span>
                                    </div>
                                    <div class="condition-cards">
                                        <div class="condition-card">
                                            <div class="condition-icon-container">
                                                <span class="condition-icon">📋</span>
                                            </div>
                                            <span class="condition-name">{medicalData.medical_conditions.other.description}</span>
                                        </div>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Medications Section -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Medications</h3>
                    <div class="medication-indicator">
                        <span class="medication-count">{medications.length}</span>
                        <span class="medication-status">{medications.length ? 'Active' : 'None'}</span>
                    </div>
                </div>
                <!-- ...existing code... -->
                <div class="section-body">
                    {#if medications.length === 0}
                        <div class="empty-state">
                            <div class="empty-icon">💊</div>
                            <p>No medications reported</p>
                        </div>
                    {:else}
                        <div class="medications-grid">
                            {#each medications as medication}
                                <div class="medication-card">
                                    <div class="medication-icon-container">
                                        <span class="medication-icon">
                                            {#if medication.includes('Diuretic')}💧
                                            {:else if medication.includes('Blood Pressure')}❤️
                                            {:else if medication.includes('Antihistamine')}🤧
                                            {:else if medication.includes('Antidepressant')}🧠
                                            {:else if medication.includes('Antipsychotic')}💫
                                            {:else}💊
                                            {/if}
                                        </span>
                                    </div>
                                    <span class="medication-name">{medication}</span>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
                <!-- ...existing code... -->
            </div><!-- Fluid Intake Section with Visual Representation -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Daily Fluid Intake</h3>
                    <div class="fluid-header-info">
                        <span class="fluid-status" class:low={hydrationStatus?.status === 'concern'} class:optimal={hydrationStatus?.status === 'good'} class:excessive={totalFluidIntake > (medicalData?.biometrics?.weight * 50)}>
                            {#if hydrationStatus?.status === 'concern'}
                                Low
                            {:else if totalFluidIntake > (medicalData?.biometrics?.weight * 50)}
                                Excessive
                            {:else if hydrationStatus?.status === 'good'}
                                Optimal
                            {:else}
                                Moderate
                            {/if}
                        </span>
                        <span class="total-ml">{totalFluidIntake} ml</span>
                    </div>
                </div>                <div class="section-body">
                    <!-- Hydration insight banner - only show when status is concern or warning -->
                    {#if hydrationStatus && ['concern', 'warning'].includes(hydrationStatus.status)}
                    <div class="insight-banner" 
                         class:concern={hydrationStatus.status === 'concern'} 
                         class:warning={hydrationStatus.status === 'warning'} 
                         class:good={hydrationStatus.status === 'good'}>
                        <div class="insight-icon">💧</div>
                        <div class="insight-content">
                            <h4>Hydration Insight</h4>
                            <p>{hydrationStatus.message}</p>
                        </div>
                    </div>
                    {/if}
                    {#if totalFluidIntake === 0}
                        <p class="no-data">No fluid intake reported</p>
                    {:else}
                        <!-- Visual representation of fluid intake -->
                        <div class="fluid-intake-modern">
                            <!-- Water level visualization -->
                            <div class="water-level-container">
                                <div class="water-level-visual">
                                    <div class="water-level" style="height: {Math.min(100, Math.max(5, (totalFluidIntake / (medicalData?.biometrics?.weight * 35)) * 100))}%"></div>
                                </div>
                                <div class="water-level-info">
                                    <span class="cups-value">{mlToCups(totalFluidIntake)} cups</span>
                                    <span class="daily-target">
                                        {#if medicalData?.biometrics?.weight}
                                            Target: {mlToCups(medicalData.biometrics.weight * 30)} cups
                                        {:else}
                                            Set weight for target
                                        {/if}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- Fluid breakdown -->
                            <div class="fluid-breakdown">
                                {#each drinkTypes as drink}
                                    {@const amount = medicalData.fluid_intake[drink.id] || 0}
                                    {#if amount > 0}
                                        <div class="fluid-item">
                                            <div class="fluid-icon-container">
                                                <span class="fluid-icon">
                                                    {#if drink.id === 'water_amount'}💧
                                                    {:else if drink.id === 'electrolyte_drinks_amount'}🧪
                                                    {:else if drink.id === 'coconut_water_amount'}🥥
                                                    {:else if drink.id === 'fruit_juice_amount'}🍊
                                                    {:else if drink.id === 'iced_tea_amount'}🍵
                                                    {:else if drink.id === 'soda_amount'}🥤
                                                    {:else if drink.id === 'milk_tea_amount'}🧋
                                                    {:else if drink.id === 'coffee_amount'}☕
                                                    {:else if drink.id === 'herbal_tea_amount'}🌿
                                                    {:else}🥛
                                                    {/if}
                                                </span>
                                            </div>
                                            <div class="fluid-details">
                                                <span class="fluid-name">{drink.label}</span>
                                                <span class="fluid-amount-modern">{amount} ml</span>
                                            </div>
                                            <div class="fluid-percentage" style="color: {drink.id === 'water_amount' ? '#0fb9b1' : '#e17055'}">
                                                {Math.round((amount / totalFluidIntake) * 100)}%
                                            </div>
                                        </div>
                                    {/if}
                                {/each}
                                
                                {#if medicalData.fluid_intake?.other_fluid && medicalData.fluid_intake?.other_fluid_amount > 0}
                                    <div class="fluid-item">
                                        <div class="fluid-icon-container">
                                            <span class="fluid-icon">🥛</span>
                                        </div>
                                        <div class="fluid-details">
                                            <span class="fluid-name">{medicalData.fluid_intake.other_fluid}</span>
                                            <span class="fluid-amount-modern">{medicalData.fluid_intake.other_fluid_amount} ml</span>
                                        </div>
                                        <div class="fluid-percentage">
                                            {Math.round((medicalData.fluid_intake.other_fluid_amount / totalFluidIntake) * 100)}%
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    {/if}
                </div>
            </div><!-- Heat Conditions Section -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Heat-Related Conditions</h3>
                    <div class="heat-indicator">
                        <span class="heat-risk-level" class:high-risk={heatConditions.length > 1} class:medium-risk={heatConditions.length === 1} class:low-risk={heatConditions.length === 0}>
                            {heatConditions.length > 1 ? 'High Risk' : heatConditions.length === 1 ? 'Medium Risk' : 'Low Risk'}
                        </span>
                    </div>
                </div>
                <!-- ...existing code... -->                <div class="section-body">
                    {#if heatConditions.length === 0}
                        <div class="empty-state">
                            <div class="empty-icon">🌡️</div>
                            <p>No heat-related conditions reported</p>
                            <span class="heat-message">Your risk for heat-related issues is low</span>
                        </div>
                    {:else}
                        <!-- Only show Heat Warning alert if there is more than one heat condition (higher risk) -->
                        {#if heatConditions.length > 1}
                        <div class="heat-warning insight-banner concern">
                            <div class="warning-icon large-icon">⚠️</div>
                            <div class="warning-text insight-content">
                                <h4>Heat Sensitivity Alert</h4>
                                <p>You have reported heat-related conditions that may increase your risk in hot environments.</p>
                            </div>
                        </div>
                        {/if}
                        <div class="heat-conditions-grid">
                            {#each heatConditions as condition}
                                <div class="heat-condition-card">
                                    <div class="condition-icon-container heat-icon">
                                        <span class="condition-icon">
                                            {#if condition.includes('Dehydration')}💧
                                            {:else if condition.includes('Rash')}🔴
                                            {:else if condition.includes('Stroke')}🔥
                                            {:else if condition.includes('Fatigue')}😩
                                            {:else if condition.includes('Syncope')}😵
                                            {:else if condition.includes('Edema')}🦶
                                            {:else if condition.includes('Exhaustion')}⚡
                                            {:else}🌡️
                                            {/if}
                                        </span>
                                    </div>
                                    <div class="heat-condition-info">
                                        <span class="condition-name">{condition}</span>
                                        <span class="condition-tip">
                                            {#if condition.includes('Dehydration')}Keep hydrated
                                            {:else if condition.includes('Rash')}Keep skin dry
                                            {:else if condition.includes('Stroke')}Seek cool areas
                                            {:else if condition.includes('Fatigue')}Rest frequently
                                            {:else if condition.includes('Syncope')}Avoid standing long
                                            {:else if condition.includes('Edema')}Elevate extremities
                                            {:else if condition.includes('Exhaustion')}Monitor symptoms
                                            {:else}Stay cool
                                            {/if}
                                        </span>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
                <!-- ...existing code... -->
            </div>

            <!-- Activity Section -->
            <div class="section-container">
                <div class="section-header">
                    <h3>Activity & Heat Issues</h3>
                    <div class="activity-indicator">
                        <span class="activity-status" 
                              class:active={medicalData.activity?.outdoor_activity && medicalData.activity?.activity_level !== 'sedentary'}
                              class:caution={medicalData.activity?.previous_heat_issues}
                              class:inactive={!medicalData.activity?.outdoor_activity || medicalData.activity?.activity_level === 'sedentary'}>
                            {medicalData.activity?.previous_heat_issues ? 'Caution' : 
                            medicalData.activity?.outdoor_activity && medicalData.activity?.activity_level !== 'sedentary' ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                </div>
                <div class="section-body">
                    <div class="activity-container">
                        <!-- Activity level visualization -->
                        {#if medicalData.activity?.outdoor_activity}
                            {@const level = medicalData.activity?.activity_level || 'sedentary'}
                                        {@const levelValue = 
                                            level === 'sedentary' ? 1 :
                                            level === 'light' ? 2 :
                                            level === 'moderate' ? 3 :
                                            level === 'vigorous' ? 4 :
                                            level === 'extreme' ? 5 : 0}
                            <div class="activity-level-container">
                                <div class="activity-visual">
                                    <div class="activity-level-header">
                                        <span class="activity-level-title">Activity Level</span>
                                        <span class="activity-level-value">{formatActivityLevel(level)}</span>
                                    </div>
                                    <div class="activity-bars">
                                        <div class="activity-bar-label">Sedentary</div>
                                        <div class="activity-bar-label">Light</div>
                                        <div class="activity-bar-label">Moderate</div>
                                        <div class="activity-bar-label">Vigorous</div>
                                        <div class="activity-bar-label">Extreme</div>
                                        
                                        <div class="activity-level-marker" style="left: {(levelValue - 0.5) * 20}%">
                                            <div class="marker-dot"></div>
                                        </div>
                                        
                                        <div class="activity-progress-bar">
                                            <div class="activity-progress" style="width: {levelValue * 20}%"></div>
                                        </div>
                                    </div>
                                    
                                    <div class="duration-tag">
                                        <span class="duration-icon">⏱️</span>
                                        <span class="duration-text">{formatActivityDuration(medicalData.activity.activity_duration)}</span>
                                    </div>
                                </div>
                            </div>
                        {:else}
                            <div class="inactive-state">
                                <div class="inactive-icon">🛋️</div>
                                <span class="inactive-text">No regular outdoor activity reported</span>
                            </div>
                        {/if}
                        
                        <!-- Previous heat issues -->
                        <div class="heat-issues-container">
                            <div class="issue-header">
                                <span class="issue-icon">{medicalData.activity?.previous_heat_issues ? '🔥' : '✅'}</span>
                                <span class="issue-title">Previous Heat Issues</span>
                                <span class="issue-status">{medicalData.activity?.previous_heat_issues ? 'Yes' : 'No'}</span>
                                {#if medicalData.activity?.previous_heat_issues && medicalData.activity?.heat_issues_details}
                                    <div class="issue-details">
                                        <p>{medicalData.activity.heat_issues_details}</p>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <!-- Closing div for medical-data -->
    {:else}
        <div class="empty-medical-profile">
            <h3>No Medical Profile Found</h3>
            <p>Please complete your medical profile to help us provide personalized hydration recommendations.</p>
            <button on:click={toggleEdit} class="submit-btn">Create Medical Profile</button>
        </div>
    {/if}
</div>

<style>
    .medical-profile {
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Section container styling - matches the account section styling */
    .section-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        background: #dd815e;
        color: white;
        padding: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .section-header h3 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
    }
    
    .section-body {
        padding: 1rem 0.75rem 1rem 0.75rem;
    }
    
    /* Fluid header info styling */
    .fluid-header-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        position: relative;
        z-index: 1;
    }
    
    .fluid-status {
        font-size: 0.85rem;
        font-weight: 600;
        color: #f0932b;
        background-color: rgba(240, 147, 43, 0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
    }
    
    .fluid-status.optimal {
        color: #0fb9b1;
        background-color: rgba(15, 185, 177, 0.2);
    }
    
    .fluid-status.low {
        color: #eb4d4b;
        background-color: rgba(235, 77, 75, 0.2);
    }
    
    .fluid-status.excessive {
        color: #8854d0;
        background-color: rgba(136, 84, 208, 0.2);
    }
    
    .total-ml {
        font-size: 0.95rem;
        font-weight: 600;
        color: white;
    }
      /* Existing styles below this line */
    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .medical-data {
        display: flex;
        flex-direction: column;
    }
    
    .data-section {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .data-section h4 {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #333;
        font-size: 1.1rem;
    }
    
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .data-item {
        display: flex;
        flex-direction: column;
    }
    
    .data-item.full-width {
        grid-column: 1 / -1;
    }
    
    .data-label {
        font-weight: 500;
        color: #666;
        margin-bottom: 0.25rem;
    }
    
    .data-value {
        font-size: 1.1rem;
    }
    
    .condition-list ul {
        list-style-type: none;
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0;
    }
    
    .condition-list li {
        background: #f0f0f0;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
    }
      /* Modern fluid intake styling */
    .no-data {
        text-align: center;
        color: #666;
        font-style: italic;
    }
    
    .fluid-intake-modern {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    /* Water level visualization */
    .water-level-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1rem;
        background-color: rgba(15, 185, 177, 0.05);
        border-radius: 12px;
    }
    
    .water-level-visual {
        width: 80px;
        height: 150px;
        background-color: #f0f0f0;
        border-radius: 40px;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
    }
    
    .water-level {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, #0fb9b1 0%, #2bcbba 100%);
        border-radius: 0;
        transition: height 1s ease;
        z-index: 1;
    }
    
    .water-level::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        animation: wave 2s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { transform: translateX(-50%); }
        50% { transform: translateX(0); }
    }
    
    .water-level-info {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .cups-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0fb9b1;
    }
    
    .daily-target {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Fluid breakdown */
    .fluid-breakdown {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .fluid-item {
        display: flex;
        align-items: center;
        padding: 0.8rem;
        background-color: #f9f9f9;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .fluid-item:hover {
        background-color: #f0f0f0;
        transform: translateX(2px);
    }
    
    .fluid-icon-container {
        width: 36px;
        height: 36px;
        background: rgba(221, 129, 94, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
    }
    
    .fluid-icon {
        font-size: 1.2rem;
    }
    
    .fluid-details {
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    
    .fluid-name {
        font-weight: 500;
        color: #333;
    }
    
    .fluid-amount-modern {
        font-size: 0.85rem;
        color: #666;
    }
    
    .fluid-percentage {
        font-size: 1rem;
        font-weight: 600;
        padding-left: 1rem;
    }
    
    /* Insight banner */
    .insight-banner {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        background-color: #f0f7ff;
        border-left: 4px solid #4a89dc;
    }
    
    .insight-banner.concern {
        background-color: #fff0f0;
        border-left-color: #dc4a4a;
    }
    
    .insight-banner.warning {
        background-color: #fffbe6;
        border-left-color: #f5d742;
    }
    
    .insight-banner.good {
        background-color: #f0fff4;
        border-left-color: #4adc7d;
    }
    
    .insight-icon {
        font-size: 1.5rem;
    }
    
    .insight-content h4 {
        margin: 0 0 0.25rem 0;
        color: #333;
    }
    
    .insight-content p {
        margin: 0;
    }
    
    /* Loading and error states */
    .loading, .error, .empty-medical-profile {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .spinner {
        display: inline-block;
        width: 30px;
        height: 30px;
        border: 3px solid rgba(0,0,0,0.1);
        border-radius: 50%;
        border-top-color: #dd815e;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 0.5rem;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .retry-btn, .submit-btn {
        background: #dd815e;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        margin-top: 1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .retry-btn:hover, .submit-btn:hover {
        background: #c26744;
    }

    /* Demographics & Biometrics modern styling */
    .bmi-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .bmi-value {
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
    }
    
    .bmi-category {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
    }
    
    .bmi-category.underweight {
        background-color: rgba(86, 130, 255, 0.2);
        color: #5682ff;
    }
    
    .bmi-category.normal {
        background-color: rgba(15, 185, 177, 0.2);
        color: #0fb9b1;
    }
    
    .bmi-category.overweight {
        background-color: rgba(240, 147, 43, 0.2);
        color: #f0932b;
    }
    
    .bmi-category.obese {
        background-color: rgba(235, 77, 75, 0.2);
        color: #eb4d4b;
    }
    
    .biometrics-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .biometrics-visual {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        background-color: #f9f9f9;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .profile-avatar {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #dd815e 0%, #e17055 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: white;
        box-shadow: 0 4px 8px rgba(221, 129, 94, 0.3);
    }
    
    .biometrics-details {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .biometrics-stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.25rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
    }
    
    .stat-unit {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.25rem;
    }
    
    .biometrics-divider {
        width: 1px;
        height: 40px;
        background-color: #e0e0e0;
    }
    
    .additional-info {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .info-card {
        flex: 1;
        min-width: 130px;
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    
    .info-icon {
        width: 40px;
        height: 40px;
        background: rgba(221, 129, 94, 0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    
    .info-content {
        display: flex;
        flex-direction: column;
    }
    
    .info-label {
        font-size: 0.8rem;
        color: #666;
    }
    
    .info-value {
        font-size: 1rem;
        font-weight: 600;
        color: #333;
    }
</style>