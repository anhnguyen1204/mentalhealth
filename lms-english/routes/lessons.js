const express = require('express');
const router = express.Router();

function requireTeacher(req, res, next) {
	if (!req.session.user || req.session.user.role !== 'TEACHER') return res.status(403).send('Forbidden');
	next();
}

router.get('/', async (req, res, next) => {
	const prisma = req.app.get('prisma');
	try {
		const lessons = await prisma.lesson.findMany({ orderBy: { createdAt: 'desc' }, include: { createdBy: true } });
		res.render('lessons/index', { lessons });
	} catch (e) { next(e); }
});

router.get('/new', requireTeacher, (req, res) => {
	res.render('lessons/new');
});

router.post('/', requireTeacher, req => req, (req, res, next) => next(), async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const upload = req.app.get('upload');
	upload.single('video')(req, res, async (err) => {
		if (err) return next(err);
		try {
			const { title, description, notes } = req.body;
			const videoPath = req.file ? `/uploads/${req.file.filename}` : null;
			await prisma.lesson.create({ data: {
				title, description, notes, videoPath,
				createdBy: { connect: { id: req.session.user.id } }
			}});
			res.redirect('/lessons');
		} catch (e) { next(e); }
	});
});

router.get('/:id', async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const id = Number(req.params.id);
	try {
		const lesson = await prisma.lesson.findUnique({ where: { id }, include: { exercises: true, createdBy: true } });
		if (!lesson) return res.status(404).send('Not found');
		res.render('lessons/show', { lesson });
	} catch (e) { next(e); }
});

router.post('/:id/delete', requireTeacher, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	try {
		await prisma.lesson.delete({ where: { id: Number(req.params.id) } });
		res.redirect('/lessons');
	} catch (e) { next(e); }
});

module.exports = router;