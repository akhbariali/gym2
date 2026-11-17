(() => {
  const activityFactors = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725 };
  const goalFactors = { lose: 0.85, maintain: 1, gain: 1.1 };

  function invalid(field, message) {
    throw Object.assign(new Error(message), { field });
  }

  function calculateHealth(input) {
    const values = {};
    for (const [field, label, min, max] of [['age', 'سن', 20, 80], ['weight', 'وزن', 35, 250], ['height', 'قد', 130, 220]]) {
      const text = String(input[field] ?? '').trim()
        .replace(/[۰-۹]/g, digit => '۰۱۲۳۴۵۶۷۸۹'.indexOf(digit))
        .replace(/[٠-٩]/g, digit => '٠١٢٣٤٥٦٧٨٩'.indexOf(digit)).replace(/٫/g, '.');
      const value = Number(text);
      if (!/^\d+(\.\d+)?$/.test(text) || !Number.isFinite(value) || value < min || value > max || (field === 'age' && !Number.isInteger(value))) {
        invalid(field, `${label} را ${field === 'age' ? 'به صورت عدد صحیح ' : ''}بین ${min.toLocaleString('fa-IR')} و ${max.toLocaleString('fa-IR')} وارد کنید.`);
      }
      values[field] = value;
    }
    if (!['male', 'female'].includes(input.sex)) invalid('sex', 'پارامتر جنسیت معادله را انتخاب کنید.');
    if (!Object.hasOwn(activityFactors, input.activity)) invalid('activity', 'سطح فعالیت را انتخاب کنید.');
    if (!Object.hasOwn(goalFactors, input.goal)) invalid('goal', 'هدف را انتخاب کنید.');

    const { age, weight, height } = values;
    const resting = 10 * weight + 6.25 * height - 5 * age + (input.sex === 'male' ? 5 : -161);
    const maintenance = resting * activityFactors[input.activity];
    const target = maintenance * goalFactors[input.goal];
    const bmi = weight / (height / 100) ** 2;
    const bmiCategory = bmi < 18.5 ? 'underweight' : bmi < 25 ? 'normal' : bmi < 30 ? 'overweight' : 'obesity';
    let calorieNote = '';
    if (input.goal === 'lose' && bmi < 18.5) calorieNote = 'با BMI کمتر از ۱۸٫۵، این ابزار هدف کاهش وزن پیشنهاد نمی‌کند. برای بررسی وضعیت تغذیه با متخصص مشورت کنید.';
    // These are conservative product guardrails, not universal minimum energy requirements.
    if (!calorieNote && target < (input.sex === 'female' ? 1200 : 1500)) calorieNote = 'برآورد کالری پایین است؛ این ابزار برای اهداف کمتر از ۱۲۰۰ در معادله زنان یا ۱۵۰۰ در معادله مردان، هدف قابل اجرا ارائه نمی‌کند. این اعداد حداقل ایمن همگانی نیستند؛ نیاز شما باید فردی بررسی شود.';
    const protein = bmi < 30 ? [Math.round(weight * 1.6), Math.round(weight * 2.2)] : null;
    return {
      resting: Math.round(resting), maintenance: Math.round(maintenance / 10) * 10,
      calories: calorieNote ? null : Math.round(target / 10) * 10,
      calorieNote, protein, perMeal: protein ? protein.map(value => Math.round(value / 4)) : null,
      proteinNote: protein ? '' : 'در BMI برابر یا بیشتر از ۳۰، ضرب پروتئین در کل وزن بدن ممکن است نیاز را بیش‌برآورد کند. این ابزار عدد شخصی پیشنهاد نمی‌کند؛ ترکیب بدن و شرایط شما باید بررسی شود.',
      bmi: Math.round(bmi * 10) / 10, bmiCategory
    };
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { calculateHealth };
  if (typeof document === 'undefined') return;
  const form = document.querySelector('#healthForm');
  if (!form) return;
  const results = document.querySelector('#healthResults');
  const error = document.querySelector('#healthError');
  const number = value => value.toLocaleString('fa-IR', { maximumFractionDigits: 1 });
  const set = (id, text) => { document.getElementById(id).textContent = text; };
  const range = values => values ? `${number(values[0])} تا ${number(values[1])} گرم` : 'نیازمند بررسی فردی';
  const categories = { underweight: 'کم‌وزنی', normal: 'محدوده معمول', overweight: 'اضافه‌وزن', obesity: 'محدوده چاقی' };
  const goals = { lose: 'شروع با ۱۵٪ کمتر از نگهدارنده', maintain: 'برآورد حفظ وزن فعلی', gain: 'شروع با ۱۰٪ بیشتر از نگهدارنده' };

  form.addEventListener('input', () => {
    results.hidden = true;
    error.textContent = '';
    form.querySelectorAll('[aria-invalid]').forEach(field => field.removeAttribute('aria-invalid'));
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    results.hidden = true;
    error.textContent = '';
    try {
      const input = Object.fromEntries(new FormData(form));
      const result = calculateHealth(input);
      set('healthCalories', result.calories === null ? 'نیازمند بررسی فردی' : `${number(result.calories)} کیلوکالری`);
      set('healthGoalNote', result.calorieNote || goals[input.goal]);
      set('healthResting', `${number(result.resting)} کیلوکالری`);
      set('healthMaintenance', `${number(result.maintenance)} کیلوکالری`);
      set('healthProtein', range(result.protein));
      set('healthProteinNote', result.proteinNote || 'مجموع پروتئین غذا و مکمل؛ برای فرد سالمی که تمرین مقاومتی دارد. مکمل الزامی نیست.');
      set('healthPerMeal', range(result.perMeal));
      set('healthBmi', `${number(result.bmi)} · ${categories[result.bmiCategory]}`);
      results.hidden = false;
      results.focus();
    } catch (failure) {
      error.textContent = failure.message;
      const field = form.elements.namedItem(failure.field);
      if (field) {
        field.setAttribute('aria-invalid', 'true');
        field.focus();
      }
    }
  });
})();
