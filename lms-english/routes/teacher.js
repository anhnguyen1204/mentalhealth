const express = require('express');
const router = express.Router();

function requireTeacher(req, res, next) {
	if (!req.session.user || req.session.user.role !== 'TEACHER') return res.status(403).send('Forbidden');
	next();
}

router.get('/', requireTeacher, (req, res) => {
	res.render('teacher/dashboard');
});

router.get('/submissions', requireTeacher, async (req, res, next) => {
	const prisma = req.app.get('prisma');
	try {
		const submissions = await prisma.response.findMany({
			orderBy: { createdAt: 'desc' },
			include: { exercise: { include: { lesson: true } }, student: true, selectedOption: true }
		});
		res.render('teacher/submissions', { submissions });
	} catch (e) { next(e); }
});

module.exports = router;