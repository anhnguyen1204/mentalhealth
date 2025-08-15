const express = require('express');
const bcrypt = require('bcryptjs');
const router = express.Router();

router.get('/signup', (req, res) => {
	res.render('auth/signup');
});

router.post('/signup', async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const { name, email, password, role } = req.body;
	try {
		const passwordHash = await bcrypt.hash(password, 10);
		const user = await prisma.user.create({ data: { name, email, passwordHash, role: role === 'TEACHER' ? 'TEACHER' : 'STUDENT' } });
		req.session.user = { id: user.id, name: user.name, email: user.email, role: user.role };
		res.redirect('/');
	} catch (err) {
		next(err);
	}
});

router.get('/login', (req, res) => {
	res.render('auth/login');
});

router.post('/login', async (req, res, next) => {
	const prisma = req.app.get('prisma');
	const { email, password } = req.body;
	try {
		const user = await prisma.user.findUnique({ where: { email } });
		if (!user) return res.status(401).render('auth/login', { error: 'Invalid credentials' });
		const ok = await bcrypt.compare(password, user.passwordHash);
		if (!ok) return res.status(401).render('auth/login', { error: 'Invalid credentials' });
		req.session.user = { id: user.id, name: user.name, email: user.email, role: user.role };
		res.redirect('/');
	} catch (err) {
		next(err);
	}
});

router.post('/logout', (req, res) => {
	req.session.destroy(() => {
		res.redirect('/');
	});
});

module.exports = router;