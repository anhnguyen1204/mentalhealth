const express = require('express');
const router = express.Router({ mergeParams: true });

function requireAuth(req, res, next) {
	if (!req.session.user) return res.redirect('/login');
	next();
}

function requireTeacher(req, res, next) {
	if (!req.session.user || req.session.user.role !== 'TEACHER') return res.status(403).send('Forbidden');
	next();
}

router.get('/new/:lessonId', requireTeacher, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	try {
		const lesson = await prisma.lesson.findUnique({ where: { id: Number(req.params.lessonId) } });
		if (!lesson) return res.status(404).send('Lesson not found');
		res.render('exercises/new', { lesson });
	} catch (e) { next(e); }
});

router.post('/', requireTeacher, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	try {
		const { lessonId, type, questionText, correctAnswer } = req.body;
		const exercise = await prisma.exercise.create({ data: {
			lessonId: Number(lessonId),
			type,
			questionText,
			correctAnswer: type === 'SHORT' ? correctAnswer || null : null
		}});
		if (type === 'MCQ') {
			const options = [req.body.optionA, req.body.optionB, req.body.optionC, req.body.optionD]
				.filter(Boolean)
				.map((text, idx) => ({ text, isCorrect: String(req.body.correctOption) === String(idx) }));
			for (const option of options) {
				await prisma.exerciseOption.create({ data: { exerciseId: exercise.id, text: option.text, isCorrect: option.isCorrect } });
			}
		}
		res.redirect(`/lessons/${lessonId}`);
	} catch (e) { next(e); }
});

router.get('/:id', requireAuth, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const id = Number(req.params.id);
	try {
		const exercise = await prisma.exercise.findUnique({
			where: { id },
			include: { options: true, lesson: true }
		});
		if (!exercise) return res.status(404).send('Not found');
		res.render('exercises/show', { exercise });
	} catch (e) { next(e); }
});

router.post('/:id/submit', requireAuth, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const exerciseId = Number(req.params.id);
	try {
		const exercise = await prisma.exercise.findUnique({ where: { id: exerciseId }, include: { options: true } });
		if (!exercise) return res.status(404).send('Not found');
		let isCorrect = null;
		let selectedOptionId = null;
		let textAnswer = null;
		if (exercise.type === 'MCQ') {
			selectedOptionId = Number(req.body.selectedOptionId);
			const selected = exercise.options.find(o => o.id === selectedOptionId);
			isCorrect = selected ? selected.isCorrect : false;
		} else {
			textAnswer = (req.body.textAnswer || '').trim();
			if (exercise.correctAnswer) {
				isCorrect = textAnswer.toLowerCase() === exercise.correctAnswer.toLowerCase();
			}
		}
		await prisma.response.create({ data: {
			exerciseId,
			studentId: req.session.user.id,
			selectedOptionId,
			textAnswer,
			isCorrect
		}});
		res.redirect(`/exercises/${exerciseId}`);
	} catch (e) { next(e); }
});

module.exports = router;